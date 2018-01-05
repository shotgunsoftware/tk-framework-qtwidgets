# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.context_editor_widget import Ui_ContextWidget

# framework imports
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")

# internal imports
shotgun_fields = sgtk.platform.current_bundle().import_module("shotgun_fields")
shotgun_menus = sgtk.platform.current_bundle().import_module("shotgun_menus")

logger = sgtk.platform.get_logger(__name__)

# fields required to create a context from a task entity without falling back to
# a SG query
TASK_QUERY_FIELDS =[
    "type",
    "id",
    "content",
    "project",
    "entity",
    "step"
]


class ContextWidget(QtGui.QWidget):
    """
    Widget which represents the current context and allows the user to search
    for a different context via search completer. A menu is also provided for
    recent contexts as well as tasks assigned to the user.

    :signal context_changed(context_obj): Fires when when the user
        selects a context.
    """

    # emitted when a settings button is clicked on a node
    context_changed = QtCore.Signal(object)

    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ContextWidget, self).__init__(parent)

        self._bundle = sgtk.platform.current_bundle()
        project = self._bundle.context.project

        # get instance of user settings to save/restore values across sessions
        self._settings = settings.UserSettings(self._bundle)

        # the key we'll use to store/retrieve recent contexts via user settings
        self._settings_recent_contexts_key = "%s_recent_contexts_%s" % (
            self._bundle.name, project["id"])

        # we will do a bg query that requires an id to catch results
        self._schema_query_id = None

        # another query to get all tasks assigned to the current user
        self._my_tasks_query_id = None

        # and a query for related tasks for a given context
        self._related_tasks_query_id = None

        # keep an in-memory cache of tasks for a given entity to prevent
        # unnecessary lookups
        self._related_tasks_cache = {}

        # keep a handle on the current context
        self._context = None

        # also keep a handle on the task manager used by completer and for
        # querying shotgun in the bg
        self._task_manager = None

        # menu for recent and user contexts
        self._task_menu = shotgun_menus.ShotgunMenu(self)
        self._task_menu.setObjectName("context_menu")
        self._task_menu.addAction("Loading...")

        # keep a handle on all actions created. the my tasks menu will be
        # constant, but the recents menu will be dynamic. so we build the menu
        # just before it is shown. these lists hold the QActions for each
        # group of contexts to show in the menu
        self._menu_actions = {
            "Related": [],
            "My Tasks": [],
            "Recent": []
        }

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)

        # Loads the style sheet for the widget
        qss_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.qss")
        with open(qss_file, "rt") as f:
            # apply to widget (and all its children)
            self.setStyleSheet(f.read())

    def eventFilter(self, widget, event):
        """
        Filter out and handle some key/click events on the search widgets.
        """

        key_event = QtCore.QEvent.KeyPress
        click_event = QtCore.QEvent.MouseButtonRelease

        if widget == self.ui.task_display:

            if event.type() == click_event:
                # user clicked on the task display, show the search widget
                self._manual_task_search_toggle(True)
                return True

        elif widget == self.ui.task_search:

            if event.type() == key_event:

                if event.key() == QtCore.Qt.Key_Escape:
                    # user escaped in the task search, show the display
                    self._manual_task_search_toggle(False)
                    return True
                elif event.key() in [
                    QtCore.Qt.Key_Tab,
                    QtCore.Qt.Key_Return,
                    QtCore.Qt.Key_Enter,
                ]:
                    # user hit tab/enter/return in search. go with the currently
                    # highlighted item or the first one
                    result = \
                        self.ui.task_search.completer().get_current_result() or\
                        self.ui.task_search.completer().get_first_result()
                    if result:
                        self._on_entity_activated(
                            result["type"],
                            result["id"],
                            result["name"],
                        )

        elif widget == self.ui.link_display:

            if event.type() == click_event:
                # user clicked on the link display, show the search widget
                self._manual_link_search_toggle(True)
                return True

        elif widget == self.ui.link_search:

            if event.type() == key_event:

                if event.key() == QtCore.Qt.Key_Escape:
                    # user escaped in the task search, show the display
                    self._manual_link_search_toggle(False)
                    return True
                elif event.key() in [
                    QtCore.Qt.Key_Tab,
                    QtCore.Qt.Key_Return,
                    QtCore.Qt.Key_Enter,
                ]:
                    # user hit tab/enter/return in search. go with the currently
                    # highlighted item or the first one
                    result = \
                        self.ui.link_search.completer().get_current_result() or\
                        self.ui.link_search.completer().get_first_result()
                    if result:
                        self._on_entity_activated(
                            result["type"],
                            result["id"],
                            result["name"],
                        )

        return False

    def save_recent_contexts(self):
        """
        Should be called by the parent widget, typically when the dialog closes,
        to ensure the recent contexts are saved to disk when closing.
        """

        # build a list of serialized recent contexts. we grab all the QActions
        # from the recents list and serialize them.
        serialized_contexts = []
        for recent_action in self._menu_actions["Recent"]:
            recent_context = recent_action.data()

            # don't include the user credentials in the serialized context as
            # it may cause issues with authentication when deserializing
            serialized_context = recent_context.serialize(
                with_user_credentials=False)

            serialized_contexts.append(serialized_context)

        logger.debug("Storing serialized 'Recent' contexts.")

        # store the recent contexts on disk. the scope is per-project
        self._settings.store(
            self._settings_recent_contexts_key,
            serialized_contexts,
            scope=settings.UserSettings.SCOPE_PROJECT
        )

    def set_context(self, context, task_display_override=None,
        link_display_override=None):
        """
        Set the context to display in the widget.

        The initial display values can be overridden via the task and link
        override args.

        :param context: Toolkit Context that the widget should be set to.
        :param str task_display_override: Override text to be displayed for the task.
        :param str link_display_override: Override text to be displayed for the link.
        """
        logger.debug("Setting context to: %s" % (context,))

        # clear any related tasks from the previous context
        self._menu_actions["Related"] = []

        self._context = context
        self._show_context(
            context,
            task_display_override=task_display_override,
            link_display_override=link_display_override
        )

        # ensure the new context is added to the list of recents.
        if context:
            self._add_to_recents(context)

    def set_up(self, task_manager):
        """
        Handles initial set up of the widget. Includes setting up menu, running
        any background set up tasks, etc.

        :param task_manager: Background task manager to use
        :type task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager`
        """
        logger.debug("Setting up the UI...")

        self._task_manager = task_manager

        # attach the context menu
        self.ui.task_menu_btn.setMenu(self._task_menu)
        self._task_menu.aboutToShow.connect(
            self._on_about_to_show_contexts_menu)

        # setup the search toggle
        self.ui.task_search_btn.toggled.connect(self._on_task_search_toggled)
        self.ui.task_search.hide()

        # setup the search toggle
        self.ui.link_search_btn.toggled.connect(self._on_link_search_toggled)
        self.ui.link_search.hide()

        # set up the task manager to the task search widget
        self.ui.task_search.set_placeholder_text("Search for Tasks...")
        self.ui.task_search.set_bg_task_manager(task_manager)
        self.ui.task_search.entity_activated.connect(
            self._on_entity_activated)

        # save as above but for the link search widget
        self.ui.link_search.set_placeholder_text("Search for entity link...")
        self.ui.link_search.set_bg_task_manager(task_manager)
        self.ui.link_search.entity_activated.connect(
            self._on_entity_activated
        )

        # limit the task autocompleter to tasks only.
        # TODO: limit to tasks linked to the entity types given
        task_types_dict = {"Task": []}
        self.ui.task_search.set_searchable_entity_types(task_types_dict)

        # set up event filters for the task/link display labels so that when
        # clicked, they go directly to an edit state
        self.ui.task_display.installEventFilter(self)
        self.ui.link_display.installEventFilter(self)

        # setup event filters for the task/link search inputs so that when
        # certain keys are pressed, the widget can react to it properly
        self.ui.task_search.installEventFilter(self)
        self.ui.link_search.installEventFilter(self)

        # we need to limit the search completer to entity types that are valid
        # for ``PublishedFile.entity`` field links. To do this, query the
        # shotgun schema to get a list of these entity types. We use the current
        # project schema if we're in a project. We do this as a background query
        # via the supplied task manager.

        # connect to the task manager signals so that we can get the results
        task_manager.task_completed.connect(self._on_task_completed)
        task_manager.task_failed.connect(self._on_task_failed)

        # query all my assigned tasks in a bg task
        self._my_tasks_query_id = task_manager.add_task(_query_my_tasks)

        # get recent contexts from user settings
        self._get_recent_contexts()

    def restrict_entity_types_by_link(self, entity_type, field_name):
        """
        Specify what entries should show up in the list of links when
        using the auto completer.

        For the simple case where you just want to show a given set of
        entity types, use :meth:`restrict_entity_types`. This method is
        a more complex restriction suitable for workflows around publishing
        and review.

        This method will look at the given link field (e.g. ``PublishedFile.entity``)
        and inspect the shotgun schema to see which entity types are valid connections
        to this field (e.g. in this example which entity types can you can associate
        a publish with) and those types will appear in the list of items shown by the
        auto completer.

        This is useful when you want to use the context widget in conjunction with
        workflows related to for example publishes, versions or notes and you want to
        restrict the entities displayed by the auto completer to the ones that have been
        configured in the shotgun site schema to be able to associate with the given type.

        :param str entity_type: Entity type to restrict based on
        :param str field_name: Shotgun field to restrict based on
        """
        if self._task_manager is None:
            raise RuntimeError("You must run set_up() before this method can be executed.")

        # Query Shotgun for valid entity types for PublishedFile.entity field
        self._schema_query_id = self._task_manager.add_task(
            _query_entity_schema,
            task_args=[entity_type, field_name]
        )

    def restrict_entity_types(self, entity_types):
        """
        Restrict which entity types should show up in the list of matches.

        :param list entity_types: List of entity types
        """
        logger.debug(
            "Restricting auto completer to show the following types: %s" % entity_types
        )
        # construct a dictionary that the search widget expects for
        # filtering. This is a dictionary with the entity types as keys and
        # values a list of search filters. We don't have any filters, so we
        # just use empty list.
        entity_types_dict = dict((k, []) for k in entity_types)

        # update the types for the link completer
        self.ui.link_search.set_searchable_entity_types(
            entity_types_dict)

    @property
    def context_label(self):
        """
        The label for the context widget.
        """
        return self.ui.label

    def set_task_tooltip(self, tooltip):
        """
        Specify a string (can be html) which should be shown
        as the tooltip for the task selection widget

        :param str tooltip: Tooltip plaintext or html
        """
        self.ui.task_display.setToolTip(tooltip)

    def set_link_tooltip(self, tooltip):
        """
        Specify a string (can be html) which should be shown
        as the tooltip for the link selection widget

        :param str tooltip: Tooltip plaintext or html
        """
        self.ui.link_display.setToolTip(tooltip)

    def enable_editing(self, enabled, message=None):
        """
        Show/hide the input widgets and display a message in the context label.

        :param bool enabled: Indicates if task/link selectors should be shown
        :param str message: Message to display on :meth:`context_label`
        """
        if enabled:
            self.ui.edit_widget.show()
        else:
            self.ui.edit_widget.hide()

        self.context_label.setText(message or "")

    def _add_to_recents(self, context):
        """
        Adds the supplied context as an action in the list of recents context
        actions
        """

        # don't add a "project" context to recents. we shouldn't encourage it
        if context.project and not context.entity and not context.task:
            return

        logger.debug("Adding context to 'Recents': %s" % (context,))

        recent_actions = self._menu_actions["Recent"]

        matching_indexes = []
        for i, recent_action in enumerate(recent_actions):
            recent_context = recent_action.data()
            if recent_context == context:
                # contexts support __eq__ so this should be enough for comparing
                matching_indexes.append(i)

        if matching_indexes:
            # context exists in recent list in one or more places. remove the
            # QAction(s) and put one of them at the front of the list
            recent_action = None
            for match_index in matching_indexes:
                recent_action = recent_actions.pop(match_index)
        else:
            # the context does not exist in the recents. add it
            recent_action = self._get_qaction_for_context(context)

        if recent_action:
            recent_actions.insert(0, recent_action)

        # only keep the 5 most recent
        self._menu_actions["Recent"] = recent_actions[:5]

    def _build_actions(self, tasks, group_name, sort=False,
        exclude_current_context=False):
        """
        Build a list of actions from the supplied tasks. The actions are stored
        in the instance's _menu_actions dictionary and used to build the menu.

        The actions will be sorted by name if ``sort`` is set to True. If the
        ``exclude_current_context`` is supplied, the widget's current context
        will not be included in the list of actions.
        """

        bundle = sgtk.platform.current_bundle()

        if not tasks:
            logger.debug("No tasks supplied for group: %s" % (group_name,))
            return

        logger.debug("Building actions for group: %s" % (group_name,))

        task_actions = []

        for task in tasks:
            task_context = bundle.sgtk.context_from_entity_dictionary(task)

            # the context from dict method clears all unnecessary fields
            # from the task upon creation. now that we have the context,
            # update the fields with the queried task fields
            task_context.task.update(task)

            # don't include the current context in this list of actions
            if (self._context and
                exclude_current_context and
                task_context == self._context):
                continue

            # build the action and add it to the list
            task_action = self._get_qaction_for_context(task_context)
            task_actions.append(task_action)

        # sort on the action text if requested
        if sort:
            task_actions.sort(key=lambda a: a.text())

        # store the actions list for use when building the menu
        self._menu_actions[group_name] = task_actions

    def _get_qaction_for_context(self, context):
        """
        Helper method to build a QAction for the supplied context.
        """

        # get the display string and icon path for the context
        context_display = _get_context_display(context, plain_text=True)
        icon_path = _get_context_icon_path(context)

        # construct the action
        action = QtGui.QAction(self)
        action.setText(context_display)
        action.setIcon(QtGui.QIcon(icon_path))
        action.setData(context)
        action.triggered.connect(
            lambda c=context: self._on_context_activated(c))

        return action

    def _get_recent_contexts(self):
        """
        Pull the stored, serialized contexts from user settings and populate the
        Recent actions list for use when building the contexts menu.
        """

        logger.debug("Retrieving stored 'Recent' actions from disk...")

        # get the serialized contexts from disk
        serialized_recent_contexts = self._settings.retrieve(
            self._settings_recent_contexts_key,
            default=[],
            scope=settings.UserSettings.SCOPE_PROJECT
        )

        # turn these into QActions to add to the list of recents in the menu
        for serialized_context in serialized_recent_contexts:
            try:
                context = sgtk.Context.deserialize(serialized_context)
            except Exception, e:
                logger.debug("Unable to deserialize stored context.")
            else:
                recent_action = self._get_qaction_for_context(context)
                self._menu_actions["Recent"].append(recent_action)

    def _manual_task_search_toggle(self, checked):
        """
        Small wrapper to manual toggle the task searching on/off
        """
        self.ui.task_search_btn.setChecked(checked)
        self.ui.task_search_btn.setDown(checked)

    def _manual_link_search_toggle(self, checked):
        """
        Small wrapper to manual toggle the link searching on/off
        """
        self.ui.link_search_btn.setChecked(checked)
        self.ui.link_search_btn.setDown(checked)

    def _on_about_to_show_contexts_menu(self):
        """
        Slot called just before the contexts menu is shown. It handles
        organizing the actions into menus.
        """

        # clear and rebuild the menu since the recents/related sections are
        # dynamic.
        self._task_menu.clear()

        bundle = sgtk.platform.current_bundle()
        project = bundle.context.project

        # ---- build the "Related" menu

        related_actions = self._menu_actions["Related"]

        if related_actions:
            self._task_menu.add_group(related_actions, "Related")

        # ---- build the "My Tasks" menu

        # TODO: here we're organizing the tasks by status. since these contexts
        # are status for a publish session, we could (perhaps should) organize
        # them once (elsewhere) and simply construct the menus here. For now,
        # this simplifies the logic since `self._menu_actions` is just a
        # dictionary of flat lists of QActions.

        my_tasks_actions = self._menu_actions["My Tasks"]

        if my_tasks_actions:

            status_groups = {}

            # organize the tasks by status
            for task_action in my_tasks_actions:
                context = task_action.data()
                task = context.task
                status_code = task.get("sg_status_list", "ip")
                status_groups.setdefault(status_code, [])
                status_groups[status_code].append(task_action)

            # special case the "ip" tasks and show them at the top level
            ip_tasks = status_groups.get("ip", [])
            top_level_my_tasks_actions = ip_tasks

            # create submenus for everything else
            for status_code in status_groups.keys():
                if status_code == "ip":
                    # skipping special cased "in progress" tasks
                    continue

                # get the display name for the status code
                status_display = shotgun_globals.get_status_display_name(
                    status_code,
                    project.get("id")
                )

                # get the actions for this code
                status_actions = status_groups[status_code]

                # build the submenu for this status
                status_menu = shotgun_menus.ShotgunMenu(self)
                status_menu.setTitle(status_display)
                status_menu.add_group(status_actions, status_display)

                # add the submenu to the top level my tasks menu
                top_level_my_tasks_actions.append(status_menu)

            self._task_menu.add_group(top_level_my_tasks_actions, "My Tasks")

        # ---- build the "Recent" menu

        recent_actions = self._menu_actions["Recent"]

        if recent_actions:
            self._task_menu.add_group(recent_actions, "Recent")

        # if there are no menu items, show a message
        if not self._task_menu.actions():
            self._task_menu.addAction("No Tasks to show")

    def _on_context_activated(self, context):
        """
        Called when a new context is set via the menu or one of the completers.
        """

        logger.debug("Context changed to: %s" % (context,))

        # update the widget to display the new context and alert listeners that
        # a new context was selected
        self._show_context(context)
        self.context_changed.emit(context)

    def _on_entity_activated(self, entity_type, entity_id, entity_name):
        """
        Slot called when an entity is selected via one of the search completers.
        """
        bundle = sgtk.platform.current_bundle()
        context = bundle.sgtk.context_from_entity(entity_type, entity_id)
        self._on_context_activated(context)

    def _on_task_search_toggled(self, checked):
        """
        Slot called when the user clicks the task display or the task search
        button.

        If checked, hides the task display label and shows the search completer.
        Also populates the completer with context info to help the user.

        If not checked, hides the search info and shows the task display widget.
        """

        if checked:

            # hide the display, show the search
            self.ui.task_display.hide()
            self.ui.task_menu_btn.hide()
            self.ui.task_search.show()
            self.ui.task_search.setFocus()

            # populate and show the completer
            if self._context:
                search_str = ""
                if self._context.entity:
                    search_str = self._context.entity["name"]
                if self._context.task:
                    search_str = "%s %s " % (
                        search_str, self._context.task["name"])
                self.ui.task_search.setText(search_str)
                self.ui.task_search.completer().search(search_str)
                self.ui.task_search.completer().complete()
        else:
            # hide the search, show the display
            self.ui.task_display.show()
            self.ui.task_menu_btn.show()
            self.ui.task_search.hide()

    def _on_link_search_toggled(self, checked):
        """
        Slot called when the user clicks the link display or the link search
        button.

        If checked, hides the link display label and shows the search completer.
        Also populates the completer with context info to help the user.

        If not checked, hides the search info and shows the link display widget.
        """

        if checked:
            # hide the display, show the search
            self.ui.link_display.hide()
            self.ui.link_search.show()
            self.ui.link_search.setFocus()

            # populate and show the completer
            if self._context:
                search_str = ""
                if self._context.entity:
                    search_str = self._context.entity["name"]
                if search_str:
                    self.ui.link_search.setText(search_str)
                    self.ui.link_search.completer().search(search_str)
                    self.ui.link_search.completer().complete()
        else:
            # hide the search, show the display
            self.ui.link_search.hide()
            self.ui.link_display.show()

    def _on_task_completed(self, task_id, group, result):
        """
        Slot called when a background task completes. Displatches methods to
        handle the results depending on which task was completed.
        """

        # queried valid entity types for PublishedFile.entity field
        if task_id == self._schema_query_id:
            logger.debug("Completed query of PublishedFile.entity schema")
            self._restrict_searchable_entity_types(result)

        # queried the current user's tasks
        elif task_id == self._my_tasks_query_id:
            logger.debug("Completed query for current user tasks.")
            self._build_actions(result, "My Tasks")

        # queried tasks related to the currently selected link
        elif task_id == self._related_tasks_query_id:
            logger.debug("Completed query for the current user's Tasks.")
            self._build_actions(
                result,
                "Related",
                sort=True,
                exclude_current_context=True
            )

    def _on_task_failed(self, task_id, group, message, traceback_str):
        """
        If the schema query fails, add a log warning. It's not catastrophic, but
        it shouldn't fail, so we need to make a record of it.
        """

        # failed to query valid entity types for PublishedFile.entity field
        if task_id == self._schema_query_id:
            logger.warn(
                "Unable to query valid entity types for PublishedFile.entity."
                "Error Message: %s.\n%s" % (message, traceback_str)
            )

        # failed to query the current user's tasks
        elif task_id == self._my_tasks_query_id:
            logger.warn(
                "Unable to query tasks for the current Shotgun user."
                "Error Message: %s.\n%s" % (message, traceback_str)
            )

        # failed to query tasks related to the currently selected link
        elif task_id == self._related_tasks_query_id:
            logger.warn(
                "Unable to related tasks for the selected entity link."
                "Error Message: %s.\n%s" % (message, traceback_str)
            )

    def _query_related_tasks(self, context):
        """
        Method called via background task to query tasks related to the current
        context's entity.
        """

        if not context.entity:
            return []

        logger.debug("Querying related tasks for context: %s" % (context,))

        # unique id for entity to use as local cache lookup
        entity_id = "%s_%s" % (
            context.entity["type"],
            context.entity["id"],
        )

        # if we've queried tasks for this entity before, just return those
        if entity_id in self._related_tasks_cache:
            return self._related_tasks_cache[entity_id]

        bundle = sgtk.platform.current_bundle()

        # query the tasks for the entity
        tasks = bundle.shotgun.find(
            "Task",
            [["entity", "is", context.entity]],
            # query all fields required to create a context from a task entity
            # dictionary. see sgtk api `context_from_entity_dictionary`
            fields=TASK_QUERY_FIELDS
        )

        # cache the tasks
        self._related_tasks_cache[entity_id] = tasks

        return tasks

    def _restrict_searchable_entity_types(self, published_file_entity_schema):
        """
        Called after successful lookup of valid PublishedFile.entity types.
        The supplied field schema contains the valid entity names. Use these to
        restrict the search completers.
        """

        # drill down into the schema to retrieve the valid types for the
        # field. this is ugly, but will ensure we get a list no matter what
        entity_types = published_file_entity_schema. \
            get("entity", {}). \
            get("properties", {}). \
            get("valid_types", {}). \
            get("value", [])

        # always include Project and Tasks
        entity_types.append("Project")

        logger.debug(
            "Limiting context link completer to these entities: %s" %
            (entity_types,)
        )

        # construct a dictionary that the search widget expects for
        # filtering. This is a dictionary with the entity types as keys and
        # values a list of search filters. We don't have any filters, so we
        # just use empty list.
        entity_types_dict = dict((k, []) for k in entity_types)

        logger.debug(
            "Setting searchable entity types to: %s" % (entity_types_dict,))

        # update the types for the link completer
        self.ui.link_search.set_searchable_entity_types(
            entity_types_dict)

        # limit the task search to tasks only.
        # TODO: limit to tasks linked to entities of the types queried above
        task_types_dict = {"Task": []}

        # now update the types for the task completer
        self.ui.task_search.set_searchable_entity_types(task_types_dict)

    def _show_context(self, context, task_display_override=None,
        link_display_override=None):
        """
        Show the supplied context in the UI.
        """

        if task_display_override:
            task_display = task_display_override
        else:
            task_display = _get_task_display(context)

        if link_display_override:
            link_display = link_display_override
        else:
            link_display = _get_link_display(context)

        # update the task display/state
        self.ui.task_display.setText(task_display)
        self.ui.task_search_btn.setChecked(False)
        self.ui.task_search_btn.setDown(False)

        # update the link display/state
        self.ui.link_display.setText(link_display)
        self.ui.link_search_btn.setChecked(False)
        self.ui.link_search_btn.setDown(False)

        if context:
            # given the context, populate any related tasks for the menu
            self._related_tasks_query_id = self._task_manager.add_task(
                self._query_related_tasks,
                task_args=[context]
            )


def _get_task_display(context, plain_text=False):
    """
    Build a display string for the task of the supplied context.

    By default, return rich text with an entity icon. If ``plain_text`` is True,
    simply return the name of the task.
    """

    if not context or not context.task:
        return ""

    task_name = context.task["name"]

    if plain_text:
        # just the name
        display_name = task_name
    else:
        # return the name with the appropriate icon in front
        task_type = context.task["type"]
        task_icon = "<img src='%s'>" % (
            shotgun_globals.get_entity_type_icon_url(task_type),)
        display_name = "%s&nbsp;%s" % (task_icon, task_name)

    return display_name


def _get_link_display(context, plain_text=False):
    """
    Build a display string for the link of the supplied context.

    By default, return rich text with an entity icon. If ``plain_text`` is True,
    simply return the name of the link.
    """

    if not context:
        return ""

    entity = context.entity or context.project or None

    if not entity:
        return ""

    entity_name = entity["name"]

    if plain_text:
        # just the name
        display_name = entity_name
    else:
        # return the name with the appropriate icon in front
        entity_type = entity["type"]
        entity_icon = "<img src='%s'>" % (
            shotgun_globals.get_entity_type_icon_url(entity_type),)
        display_name = "%s&nbsp;%s" % (entity_icon, entity_name)

    return display_name


def _get_context_display(context, plain_text=False):
    """
    Return the full display string for the supplied context.

    By default, return rich text with entity icons. If ``plain_text`` is True,
    simply return the display text for link > task.
    """

    # individual display of task/link
    task_display = _get_task_display(context, plain_text=plain_text)
    link_display = _get_link_display(context, plain_text=plain_text)

    # always show link (entity)
    display_name = link_display

    # include task if there is one
    if task_display:

        if plain_text:
            display_name = "%s > %s" % (display_name, task_display)
        else:
            display_name = """
                %s&nbsp;&nbsp;<b><code>&gt;</code></b>&nbsp;&nbsp;%s
            """ % (link_display, task_display)

    return display_name


def _get_context_icon_path(context):
    """
    Get the most appropriate icon for a given context.
    """

    # We use the context's entity icon primarily since the task icon is a
    # checkmark and looks wonky in menus (where this is primarily called from).

    if context.entity:
        entity_type = context.entity["type"]
        return shotgun_globals.get_entity_type_icon_url(entity_type)
    elif context.task:
        return shotgun_globals.get_entity_type_icon_url("Task")
    elif context.project:
        return shotgun_globals.get_entity_type_icon_url("Project")
    else:
        return ""


def _query_my_tasks():
    """
    Called via bg task to query SG for tasks assigned to the current user.
    """

    bundle = sgtk.platform.current_bundle()
    project = bundle.context.project
    current_user = bundle.context.user

    logger.debug("Querying tasks for the curren user: %s" % (current_user,))

    filters = [
        ["project", "is", project],
        ["task_assignees", "is", current_user],
    ]

    order = [
        {"field_name": "entity", "direction": "asc"},
        {"field_name": "content", "direction": "asc"}
    ]

    # query all fields required to create a context from a task entity
    # dictionary. see sgtk api `context_from_entity_dictionary`
    task_fields = TASK_QUERY_FIELDS
    task_fields.extend(["sg_status_list"])

    return bundle.shotgun.find(
        "Task",
        filters,
        fields=task_fields,
        order=order
    )


def _query_entity_schema(entity_type, field_name):
    """
    Called as bg task to query SG for the field schema
    for the given type and field.

    :param str entity_type: Entity type to query schema for
    :param str field_name: Shotgun field name to query schema for
    """
    logger.debug("Querying %s.%s schema..." % (entity_type, field_name))

    bundle = sgtk.platform.current_bundle()
    project = bundle.context.project

    return bundle.shotgun.schema_field_read(
        entity_type,
        field_name=field_name,
        project_entity=project
    )
