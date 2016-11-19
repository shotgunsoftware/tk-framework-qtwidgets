# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
This module implements a QMenu subclass that knows how to display all the fields
for a given Shotgun entity type.

An example of how to use it is:

    class AppDialog(QtGui.QWidget):
        def __init__(self):
            QtGui.QWidget.__init__(self)

            # grab a field manager to know what fields are displayable
            self._field_manager = shotgun_fields.ShotgunFieldManager()

            # setup a label to have the fields menu as its context menu
            self.label = QtGui.QLabel("Right click me!")
            self.label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.label.customContextMenuRequested.connect(self.open_menu)

            # and layout the dialog
            layout = QtGui.QVBoxLayout(self)
            layout.addWidget(self.label)
            self.setLayout(layout)

        def field_filter(self, field):
            # display fields that are displayable by the shotgun field widgets
            return bool(self._field_manager.supported_fields("CustomEntity02", [field]))

        def open_menu(self, position):
            menu = shotgun_menus.EntityFieldMenu("CustomEntity02")

            # attach our filters
            menu.set_field_filter(self.field_filter)
            menu.set_checked_filter(self.checked_filter)
            menu.set_disabled_filter(self.disabled_filter)

            # show the menu and print the result
            action = menu.exec_(self.label.mapToGlobal(position))
            if action:
                # action's data has the field that was selected
                self.do_thing(action.data()["field"])
"""
import sgtk
from sgtk.platform.qt import QtGui

from .shotgun_menu import ShotgunMenu

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class EntityFieldMenu(ShotgunMenu):
    """
    A menu that automatically displays the fields for a given Shotgun entity.

    The QActions for the menu will all have their data set to a dictionary in the form:
        {"field": selected_field}
    """
    _AUDIT_FIELDS = ["created_by", "created_at", "updated_by", "updated_at"]

    def __init__(self, sg_entity_type, parent=None, bg_task_manager=None, project_id=None):
        """
        Constructor

        :param sg_entity_type: The entity type to build a menu for
        :type sg_entity_type: String

        :param parent: Parent widget
        :type parent: :class:`~PySide.QtGui.QWidget`

        :param bg_task_manager: The task manager the menu will use if it needs to run a task
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`

        :param int project_id: The project Entity id. If None, the current
                               context's project will be used, or the "site"
                               cache location will be returned if the current
                               context does not have an associated project.
        """
        super(EntityFieldMenu, self).__init__(parent)

        self._bundle = sgtk.platform.current_bundle()
        self._sg_entity_type = sg_entity_type

        # default state
        self._field_filter = None
        self._checked_filter = None
        self._disabled_filter = None
        self._entity_type_filter = None
        self._project_id = project_id or self._get_current_project_id()

        # prefix for fields if this menu represents an entity bubbled through another field
        self._bubble_base = None

        self._owns_task_manager = False
        self._task_manager = bg_task_manager
        if self._task_manager is None:
            self._owns_task_manager = True

            task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")
            self._task_manager = task_manager.BackgroundTaskManager(
                parent=self,
                max_threads=1,
                start_processing=True
            )

        # populate the menu the first time it is shown
        self._initialized = False
        self.aboutToShow.connect(self._on_about_to_show)

    def set_field_filter(self, field_filter):
        """
        Set the callback used to filter which fields are shown by the menu.

        :param field_filter: Callback called for each entity field which returns True if the field
            should be shown and False if it should not.  The fields will be in "bubbled" notation,
            for example "sg_sequence.Sequence.code"
        :type field_filter: A method that takes a single field string as its only argument and
            returns a boolean
        """
        self._field_filter = field_filter

    def set_checked_filter(self, checked_filter):
        """
        Set the callback used to set which fields are checked.  By specifying a value other than
        None, all the menu items will be checkable.

        :param checked_filter: Callback called for each entity field which returns True if the field
            should be checked and False if it should not.  The fields will be in "bubbled" notation,
            for example "sg_sequence.Sequence.code"
        :type checked_filter: A method that takes a single field string as its only argument and
            returns a boolean
        """
        self._checked_filter = checked_filter

    def set_disabled_filter(self, disabled_filter):
        """
        Set the callback used to filter which fields are disabled

        :param disabled_filter: Callback called for each entity field which returns True if the field
            should be disabled and False if it should not.  The fields will be in "bubbled" notation,
            for example "sg_sequence.Sequence.code"
        :type disabled_filter: A method that takes a single field string as its only argument and
            returns a boolean
        """
        self._disabled_filter = disabled_filter

    def set_entity_type_filter(self, entity_type_filter):
        """
        Set the callback used to filter what entity types to display in submenus

        :param entity_type_filter: Callback called for each entity type which returns True if the
            given entity type should be displayed
        :type entity_type_filter: A method that takes a single entity types string as its only argument
            and returns a boolean
        """
        self._entity_type_filter = entity_type_filter

    def __del__(self):
        """
        Destructor
        """
        if self._owns_task_manager:
            shotgun_globals.unregister_bg_task_manager(self._task_manager)

    def _on_about_to_show(self):
        """
        Lazy load the menu.  This is because it is possible to have cycles when traversing
        through the possible bubbled fields, so it is impossible to build the entire nested menu.
        """
        if not self._initialized:
            # need to wait until there is a schema available before populating the menu
            shotgun_globals.run_on_schema_loaded(
                self._populate, project_id=self._project_id)
            self._initialized = True

    def _populate(self):
        """
        Build the menu
        """
        field_infos = []
        bubble_fields = {}

        # gather needed field info
        for field in shotgun_globals.get_entity_fields(
                self._sg_entity_type, project_id=self._project_id):

            # convert field to bubbled form
            bubbled_field = self._get_bubbled_name(field)

            # apply any needed filtering
            if self._field_filter and not self._field_filter(bubbled_field):
                continue

            # grab display names
            display_name = shotgun_globals.get_field_display_name(
                self._sg_entity_type,
                field,
                project_id=self._project_id,
            )
            field_infos.append({"field": field, "name": display_name, "bubbled": bubbled_field})

            # grab info to build bubbled menu
            try:
                # grab the entity types this field can bubble to
                entity_types = shotgun_globals.get_valid_types(
                    self._sg_entity_type,
                    field,
                    project_id=self._project_id,
                )

                # filter out entities via the registered callback
                if self._entity_type_filter:
                    entity_types = [t for t in entity_types if self._entity_type_filter(t)]

                # and filter out any entities that don't have any displayable fields
                if self._field_filter:
                    def entity_filter(et):
                        # get the list of fields for this entity type
                        fields = shotgun_globals.get_entity_fields(
                            et, project_id=self._project_id)

                        # and filter them down with the filter
                        if self._field_filter:
                            fields = [f for f in fields if self._field_filter("%s.%s.%s" % (bubbled_field, et, f))]

                        return bool(fields)
                    entity_types = [et for et in entity_types if entity_filter(et)]

                if entity_types:
                    bubble_fields[field] = {
                        "name": display_name,
                        "valid_types": entity_types,
                        "valid_type_names": [
                            shotgun_globals.get_type_display_name(
                                et,
                                project_id=self._project_id,
                            ) for et in entity_types
                        ],
                        "bubbled_bases": ["%s.%s" % (bubbled_field, et) for et in entity_types],
                    }
            except Exception:
                # not a field that can be bubbled
                pass

        # sort by display name
        field_infos.sort(key=lambda item: item["name"])

        # add in all fields other than audit fields
        audit_fields = []
        bubbled_actions = []
        for field_info in field_infos:
            if field_info["field"] in self._AUDIT_FIELDS:
                audit_fields.append(field_info)
            else:
                bubbled_actions.append(
                    self._get_qaction(field_info["bubbled"], field_info["name"]))
        if bubbled_actions:
            self.add_group(bubbled_actions)

        # now the audit fields
        if audit_fields:
            audit_actions = []
            for field_info in audit_fields:
                audit_actions.append(
                    self._get_qaction(field_info["field"], field_info["name"]))
            if audit_actions:
                self.add_group(audit_actions, title="Audit Fields")

        # and finally bubble fields
        if bubble_fields:

            linked_menus = []
            for (field, field_info) in bubble_fields.iteritems():
                # pull all the bubbled field data in an order that sorts by display name
                sorted_items = sorted(
                    zip(
                        field_info["valid_type_names"],
                        field_info["valid_types"],
                        field_info["bubbled_bases"],
                    )
                )

                entity_menus = []
                for (type_name, entity_type, bubble_base) in sorted_items:
                    # build the menu for this entity passing on our state
                    entity_menu = EntityFieldMenu(entity_type, parent=self, bg_task_manager=self._task_manager)
                    entity_menu.set_field_filter(self._field_filter)
                    entity_menu.set_disabled_filter(self._disabled_filter)
                    entity_menu.set_checked_filter(self._checked_filter)
                    entity_menu._bubble_base = bubble_base

                    # keep track of the menus we built and what the display name for it would be
                    entity_menus.append((type_name, entity_menu))

                if len(entity_menus) == 1:
                    # if there is only one type of entity possible, add the menu directly
                    entity_menu = entity_menus[0][1]
                    entity_menu.setTitle(field_info["name"])
                    linked_menus.append(entity_menu)
                elif len(entity_menus) > 1:
                    # otherwise add an intermediate menu for each possible entity type
                    bubble_menu = QtGui.QMenu(field_info["name"])
                    for (type_name, entity_menu) in entity_menus:
                        entity_menu.setTitle(type_name)
                        bubble_menu.addMenu(entity_menu)
                    linked_menus.append(bubble_menu)

            self.add_group(linked_menus, title="Linked Fields")

    def _get_bubbled_name(self, field_name, bubble_base=None):
        """
        Translate the given field name into a bubbled name.  This will prepend the bubble string
        that translates the given field name into a string that can be used to reach the field
        from the entity associated with the root menu.

        :param field_name: The non-bubbled Shotgun field name
        :type field_name: String
        """
        if bubble_base is None:
            bubble_base = self._bubble_base

        if bubble_base:
            return "%s.%s" % (bubble_base, field_name)
        return field_name

    def _get_qaction(self, field, display_name):
        """
        Add an action for the given field to the menu. The data for the action will contain
        a dictionary where the selected field is set for the "field" key.

        :param field: The field to add, in bubbled notation (eg 'entity.Shot.code')
        :type field: String

        :param display_name: The text to display for the action
        :type display_name: String
        """
        action = QtGui.QAction(display_name, self)

        action.setData({
            "field": field,
        })

        if self._checked_filter:
            action.setCheckable(True)
            action.setChecked(self._checked_filter(field))
        else:
            action.setCheckable(False)

        if self._disabled_filter:
            action.setDisabled(self._disabled_filter(field))

        return action

    def _get_current_project_id(self):
        """
        Return the id of the current project.

        :returns: The project id associated with the current context, or ``None``
            if operating in a site-level context.
        :rtype: ``int`` or ``None``
        """

        if self._bundle.tank.pipeline_configuration.is_site_configuration():
            # site configuration (no project id). Return None which is
            # consistent with core.
            project_id = None
        else:
            project_id = self._bundle.tank.pipeline_configuration.get_project_id()

        return project_id

