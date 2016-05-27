# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import json
import sgtk

from sgtk.platform.qt import QtCore, QtGui

from .ui.version_details_widget import Ui_VersionDetailsWidget
from .selection_context_menu import SelectionContextMenu

from .qtwidgets import (
    ShotgunEntityCardDelegate,
    ShotgunFieldManager,
    EntityFieldMenu,
    ShotgunSortFilterProxyModel,
    SimpleTooltipModel,
)

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_model",
)

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_globals",
)

task_manager = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "task_manager",
)

shotgun_data = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_data",
)

settings = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "settings",
)

class VersionDetailsWidget(QtGui.QWidget):
    FIELDS_PREFS_KEY = "version_details_fields"
    ACTIVE_FIELDS_PREFS_KEY = "version_details_active_fields"
    VERSION_LIST_FIELDS_PREFS_KEY = "version_details_version_list_fields"

    # Emitted when an entity is created by the panel. The
    # entity type as a string and id as an int are passed
    # along.
    entity_created = QtCore.Signal(object)

    # The int is the id of the Note entity that was selected or deselected.
    note_selected = QtCore.Signal(int)
    note_deselected = QtCore.Signal(int)

    def __init__(self, bg_task_manager, parent=None, entity=None):
        """
        Constructs a new :class:`~VersionDetailsWidget` object.

        :param parent:          The widget's parent.
        :param bg_task_manager: A :class:`~BackgroundTaskManager` object.
        :param entity:          A Shotgun Version entity dictionary.
        """
        super(VersionDetailsWidget, self).__init__(parent)

        self._current_entity = None
        self._pinned = False
        self._requested_entity = None
        self._sort_versions_ascending = False
        self._upload_task_ids = []
        self._task_manager = bg_task_manager
        self._version_context_menu_actions = []

        self.ui = Ui_VersionDetailsWidget() 
        self.ui.setupUi(self)

        # Show the "empty" image that tells the user that no Version
        # is active.
        self.ui.pages.setCurrentWidget(self.ui.empty_page)

        self._data_retriever = shotgun_data.ShotgunDataRetriever(
            parent=self,
            bg_task_manager=self._task_manager,
        )

        self._shotgun_field_manager = ShotgunFieldManager(
            self,
            bg_task_manager=self._task_manager,
        )

        self._settings_manager = settings.UserSettings(
            sgtk.platform.current_bundle(),
        )

        shotgun_globals.register_bg_task_manager(self._task_manager)
        self._shotgun_field_manager.initialize()

        # These are the minimum required fields that we need
        # in order to draw all of our widgets with default settings.
        self._fields = [
            "image",
            "user",
            "project",
            "code",
            "id",
            "entity",
            "sg_status_list",
        ]

        prefs_fields = self._settings_manager.retrieve(
            VersionDetailsWidget.FIELDS_PREFS_KEY,
            [],
            self._settings_manager.SCOPE_ENGINE,
        )

        self._fields.extend([f for f in prefs_fields if f not in self._fields])

        # These are the fields that have been given to the info widget
        # at the top of the Notes tab. This represents all fields that
        # are displayed by default when the "More info" option is active.
        self._active_fields = self._settings_manager.retrieve(
            VersionDetailsWidget.ACTIVE_FIELDS_PREFS_KEY,
            [
                "code",
                "entity",
                "user",
                "sg_status_list",
            ],
            self._settings_manager.SCOPE_ENGINE,
        )

        # This is the subset of self._active_fields that are always
        # visible, even when "More info" is not active.
        self._persistent_fields = [
            "code",
            "entity",
        ]

        # The fields list for the Version list view delegate operate
        # the same way as the above persistent list. We're simply
        # keeping track of what we don't allow to be turned off.
        self._version_list_persistent_fields = [
            "code",
            "user",
            "sg_status_list",
        ]

        # Our sort-by list will include "id" at the head.
        self._version_list_sort_by_fields = ["id"] + self._version_list_persistent_fields

        self.version_model = SimpleTooltipModel(
            self.ui.entity_version_tab,
            bg_task_manager=self._task_manager,
        )
        self.version_proxy_model = ShotgunSortFilterProxyModel(
            parent=self.ui.entity_version_view,
        )
        self.version_proxy_model.filter_by_fields = self._version_list_persistent_fields
        self.version_proxy_model.sort_by_fields = self._version_list_sort_by_fields
        self.version_proxy_model.setFilterWildcard("*")
        self.version_proxy_model.setSourceModel(self.version_model)
        self.ui.entity_version_view.setModel(self.version_proxy_model)
        self.version_delegate = ShotgunEntityCardDelegate(
            view=self.ui.entity_version_view,
            shotgun_field_manager=self._shotgun_field_manager,
        )
        self.version_delegate.fields = self._settings_manager.retrieve(
            VersionDetailsWidget.VERSION_LIST_FIELDS_PREFS_KEY,
            self._version_list_persistent_fields,
            self._settings_manager.SCOPE_ENGINE,
        )
        self.version_delegate.label_exempt_fields = ["code"]
        self.ui.entity_version_view.setItemDelegate(self.version_delegate)
        self.ui.note_stream_widget.set_bg_task_manager(self._task_manager)
        self.ui.note_stream_widget.show_sg_stream_button = False
        self.ui.note_stream_widget.version_items_playable = False
        self.version_info_model = shotgun_model.SimpleShotgunModel(
            self.ui.note_stream_widget,
            bg_task_manager=self._task_manager,
        )

        # For the basic info widget in the Notes stream we won't show
        # labels for the fields that are persistent. The non-standard,
        # user-specified list of fields that are shown when "more info"
        # is active will be labeled.
        self.ui.current_version_card.field_manager = self._shotgun_field_manager
        self.ui.current_version_card.fields = self._active_fields
        self.ui.current_version_card.label_exempt_fields = self._persistent_fields

        # Signal handling.
        self.ui.pin_button.toggled.connect(self.set_pinned)
        self.ui.more_info_button.toggled.connect(self._more_info_toggled)
        self.ui.shotgun_nav_button.clicked.connect(
            self.ui.note_stream_widget._load_shotgun_activity_stream
        )
        self.ui.entity_version_view.customContextMenuRequested.connect(
            self._show_version_context_menu,
        )
        self.ui.version_search.search_edited.connect(self._set_version_list_filter)
        self.version_info_model.data_refreshed.connect(self._version_entity_data_refreshed)
        self._task_manager.task_group_finished.connect(self.ui.entity_version_view.update)
        self._data_retriever.work_completed.connect(self.__on_worker_signal)
        self.ui.note_stream_widget.note_selected.connect(self.note_selected.emit)
        self.ui.note_stream_widget.note_deselected.connect(self.note_deselected.emit)

        # We're taking over the responsibility of handling the title bar's
        # typical responsibilities of closing the dock and managing float
        # and unfloat behavior. We need to hook up to the dockLocationChanged
        # signal because a floating DockWidget can be redocked with a
        # double click of the window, which won't go through our button.
        self.ui.float_button.clicked.connect(self._toggle_floating)
        self.ui.close_button.clicked.connect(self._hide_dock)

        # We will be passing up our own signal when note and reply entities
        # are created.
        self.ui.note_stream_widget.entity_created.connect(
            self._entity_created,
        )

        # The fields menu attached to the "Fields..." buttons
        # when "More info" is active as well as in the Versions
        # tab.
        self._setup_fields_menu()
        self._setup_version_list_fields_menu()
        self._setup_version_sort_by_menu()

        if entity:
            self.load_data(entity)

        self._load_stylesheet()

        # This will handle showing or hiding the dock title bar
        # depending on what the parent is.
        self.setParent(parent)

    ##########################################################################
    # properties

    @property
    def current_entity(self):
        """
        The current Shotgun entity that is active in the widget.
        """
        return self._current_entity

    @property
    def is_pinned(self):
        """
        Returns True if the panel is pinned and not processing entity
        updates, and False if it is not pinned.
        """
        return self._pinned

    ##########################################################################
    # public methods

    def add_note_attachments(self, file_paths, note_entity, cleanup_after_upload=True):
        """
        Adds a given list of files to the note widget as file attachments.

        :param file_paths:              A list of file paths to attach to the
                                        current note.
        :param cleanup_after_upload:    If True, after the files are uploaded
                                        to Shotgun they will be removed from disk.
        """
        if note_entity["type"] == "Reply":
            note_entity = note_entity["entity"]

        for file_path in file_paths:
            self._upload_uid = self._data_retriever.execute_method(
                self._upload_file,
                dict(
                    file_path=file_path,
                    parent_entity_type=note_entity["type"],
                    parent_entity_id=note_entity["id"],
                    cleanup_after_upload=cleanup_after_upload,
                ),
            )

    def add_query_fields(self, fields):
        """
        Adds the given list of Shotgun field names to the list of fields
        that are queried by the version details widget's internal data
        model. Adding fields this way does not change the display of
        information about the entity in any way.

        :param fields:  A list of Shotgun field names to add.
        :type fields:   [field_name, ...]
        """
        self._fields.extend([f for f in fields if f not in self._fields])

    def add_version_context_menu_action(self, action_definition):
        """
        Adds an action to the version tab's context menu.

        Action definitions passed in must take the following form:

            dict(
                callback=callable,
                text=str,
                required_selection="single"
            )

        Where the callback is a callable object that expects to receive
        a list of Version entity dictionaries as returned by the Shotgun
        Python API. The text key contains the string labels of the action
        in the QMenu, and the required_selection is one of "single", "multi",
        or "either". Any action requiring a "single" selection will be enabled
        only if there is a single item selected in the Version list view,
        those requiring "multi" selection require 2 or more selected items,
        and the "either" requirement results in the action being enabled if
        one or more items are selected.

        :param action_definition:   The action defition to add to the menu.
                                    This takes the form of a dictionary of
                                    a structure described in the method docs
                                    above.
        :type action_definition:    dict
        """
        self._version_context_menu_actions.append(action_definition)

    def clear(self):
        """
        Clears all data from all widgets and views in the details panel.
        """
        self._more_info_toggled(False)
        self.ui.note_stream_widget._clear()
        self.ui.current_version_card.clear()
        self.ui.pages.setCurrentWidget(self.ui.empty_page)
        self.version_model.clear()
        self._requested_entity = None
        self._current_entity = None

    def load_data(self, entity):
        """
        Loads the given Shotgun entity into the details panel,
        triggering the notes and versions streams to be updated
        relative to the given entity.

        :param entity:  The Shotgun entity to load. This is a dict in
                        the form returned by the Shotgun Python API.
        """
        self._requested_entity = entity

        # If we're pinned, then we don't allow loading new entities.
        if self._pinned and self.current_entity:
            return

        # If we got an "empty" entity from the mode, then we need
        # to clear everything out and go back to an empty state.
        if not entity or not entity.get("id"):
            self.clear()
            return

        # Switch over to the page that contains the primary display
        # widget set now that we have data to show.
        self.ui.pages.setCurrentWidget(self.ui.main_page)

        # If there aren't any fields set in the info widget then it
        # likely means we're loading from a "cleared" slate and need
        # to re-add our relevant fields.
        if not self.ui.current_version_card.fields:
            self.ui.current_version_card.fields = self._active_fields
            self.ui.current_version_card.label_exempt_fields = self._persistent_fields

        self.ui.note_stream_widget.load_data(entity)

        shot_filters = [["id", "is", entity["id"]]]
        self.version_info_model.load_data(
            entity_type="Version",
            filters=shot_filters,
            fields=self._fields,
        )

    def save_preferences(self):
        """
        Saves user preferences to disk.
        """
        self._settings_manager.store(
            VersionDetailsWidget.FIELDS_PREFS_KEY,
            self._fields,
            self._settings_manager.SCOPE_ENGINE,
        )

        self._settings_manager.store(
            VersionDetailsWidget.ACTIVE_FIELDS_PREFS_KEY,
            self._active_fields,
            self._settings_manager.SCOPE_ENGINE,
        )

        self._settings_manager.store(
            VersionDetailsWidget.VERSION_LIST_FIELDS_PREFS_KEY,
            self.version_delegate.fields,
            self._settings_manager.SCOPE_ENGINE,
        )

    def set_note_screenshot(self, image_path):
        """
        Takes the given file path to an image and sets the new note
        widget's thumbnail image.

        :param image_path:  A file path to an image file on disk.
        """
        self.ui.note_stream_widget.note_widget._set_screenshot_pixmap(
            QtGui.QPixmap(image_path),
        )

    def setParent(self, parent):
        """
        Calls the base class' method of the same name, and then checks
        to see if the parent is a dock widget. If it is, then a custom
        title bar is made visible.
        """
        super(VersionDetailsWidget, self).setParent(parent)

        try:
            self.parent().dockLocationChanged.connect(self._dock_location_changed)
            self._dock_location_changed()
        except Exception:
            # If we're not in a dock widget, then we shouldn't show the
            # title bar with dock and close buttons.
            self.show_title_bar_buttons(False)
        else:
            self.show_title_bar_buttons(True)

    def set_pinned(self, checked):
        """
        Sets the "pinned" state of the details panel. When the panel is
        pinned it will not accept updates. It will, however, record the
        most recent entity passed to load_data that was not accepted. If
        the panel is unpinned at a later time, the most recent rejected
        entity update will be executed at that time.

        :param checked: True or False
        """
        self._pinned = checked

        if checked:
            self.ui.pin_button.setIcon(QtGui.QIcon(":/version_details/tack_hover.png"))
        else:
            self.ui.pin_button.setIcon(QtGui.QIcon(":/version_details/tack_up.png"))
            if self._requested_entity:
                self.load_data(self._requested_entity)

    def show_title_bar_buttons(self, state):
        """
        Sets the visibility of the undock and close buttons in the
        widget's title bar.

        :param state:   Whether to show or hide the buttons.
        :type state:    bool
        """
        self.ui.float_button.setVisible(state)
        self.ui.close_button.setVisible(state)

    ##########################################################################
    # internal utilities

    def _load_stylesheet(self):
        """
        Loads in the widget's master stylesheet from disk.
        """
        qss_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "style.qss"
        )
        try:
            f = open(qss_file, "rt")
            qss_data = sgtk.platform.current_bundle().engine._resolve_sg_stylesheet_tokens(
                f.read(),
            )
            self.setStyleSheet(qss_data)
        finally:
            f.close()

    def _entity_created(self, entity):
        """
        Emits the entity_created signal.

        :param entity: The Shotgun entity dict that was created.
        """
        self.entity_created.emit(entity)

    def _field_menu_triggered(self, action):
        """
        Adds or removes a field when it checked or unchecked
        via the EntityFieldMenu.

        :param action:  The QMenuAction that was triggered. 
        """
        if action:
            # The MenuAction's data will have a "field" key that was
            # added by the EntityFieldMenu that contains the name of
            # the field that was checked or unchecked.
            field_name = action.data()["field"]

            if action.isChecked():
                self.ui.current_version_card.add_field(field_name)
                self._fields.append(field_name)
                self.load_data(self._requested_entity)
            else:
                self.ui.current_version_card.remove_field(field_name)

            self._active_fields = self.ui.current_version_card.fields

            try:
                self._settings_manager.store(
                    VersionDetailsWidget.FIELDS_PREFS_KEY,
                    self._fields,
                    self._settings_manager.SCOPE_ENGINE,
                )
                self._settings_manager.store(
                    VersionDetailsWidget.ACTIVE_FIELDS_PREFS_KEY,
                    self._active_fields,
                    self._settings_manager.SCOPE_ENGINE,
                )
            except Exception:
                pass

    def _version_entity_data_refreshed(self):
        """
        Takes the currently-requested entity and sets various widgets
        to display it.
        """
        entity = self._requested_entity
        item = self.version_info_model.item_from_entity(
            "Version",
            entity["id"],
        )

        if not item:
            return

        sg_data = item.get_sg_data()

        self.ui.current_version_card.entity = sg_data
        self._more_info_toggled(self.ui.more_info_button.isChecked())

        if sg_data.get("entity"):
            version_filters = [["entity", "is", sg_data["entity"]]]
            self.version_model.load_data(
                "Version",
                filters=version_filters,
                fields=self._fields,
            )

            self.version_proxy_model.sort(
                0, 
                (
                    QtCore.Qt.AscendingOrder if 
                    self._sort_versions_ascending else 
                    QtCore.Qt.DescendingOrder
                ),
            )
        else:
            self.version_model.clear()

        self._current_entity = sg_data
        self._setup_fields_menu()
        self._setup_version_list_fields_menu()
        self._setup_version_sort_by_menu()

    def _version_list_field_menu_triggered(self, action):
        """
        Adds or removes a field when it checked or unchecked
        via the EntityFieldMenu.

        :param action:  The QMenuAction that was triggered. 
        """
        if action:
            # The MenuAction's data will have a "field" key that was
            # added by the EntityFieldMenu that contains the name of
            # the field that was checked or unchecked.
            field_name = action.data()["field"]

            if action.isChecked():
                self.version_delegate.add_field(field_name)

                # When a field is added to the list, then we also need to
                # add it to the sort-by menu.
                if field_name not in self._version_list_sort_by_fields:
                    self._version_list_sort_by_fields.append(field_name)
                    self._fields.append(field_name)
                    self.load_data(self._requested_entity)

                    new_action = QtGui.QAction(
                        shotgun_globals.get_field_display_name(
                            "Version",
                            field_name,
                        ),
                        self,
                    )

                    new_action.setData(field_name)
                    new_action.setCheckable(True)

                    self._version_sort_menu_fields.addAction(new_action)
                    self._version_sort_menu.addAction(new_action)
                    self._sort_version_list()
            else:
                self.version_delegate.remove_field(field_name)

                # We also need to remove the field from the sort-by menu. We
                # will leave "id" in the list always, even if it isn't being
                # displayed by the delegate.
                if field_name != "id" and field_name in self._version_list_sort_by_fields:
                    self._version_list_sort_by_fields.remove(field_name)
                    sort_actions = self._version_sort_menu.actions()
                    remove_action = [a for a in sort_actions if a.data() == field_name][0]

                    # If it's the current primary sort field, then we need to
                    # fall back on "id" to take its place.
                    if remove_action.isChecked():
                        actions = self._version_sort_menu_fields.actions()
                        id_action = [a for a in actions if a.data() == "id"][0]
                        id_action.setChecked(True)
                        self._sort_version_list(id_action)
                    self._version_sort_menu.removeAction(remove_action)
                    self._version_sort_menu_fields.removeAction(remove_action)

            self.version_proxy_model.filter_by_fields = self.version_delegate.fields
            self.version_proxy_model.setFilterWildcard(self.ui.version_search.search_text)
            self.ui.entity_version_view.repaint()

            try:
                self._settings_manager.store(
                    VersionDetailsWidget.FIELDS_PREFS_KEY,
                    self._fields,
                    self._settings_manager.SCOPE_ENGINE,
                )
                self._settings_manager.store(
                    VersionDetailsWidget.VERSION_LIST_FIELDS_PREFS_KEY,
                    self.version_delegate.fields,
                    self._settings_manager.SCOPE_ENGINE,
                )
            except Exception:
                pass

    def _more_info_toggled(self, checked):
        """
        Toggled more/less info functionality for the info widget in the
        Notes tab.

        :param checked: True or False
        """
        if checked:
            self.ui.more_info_button.setText("Hide info")
            self.ui.more_fields_button.show()

            for field_name in self._active_fields:
                self.ui.current_version_card.set_field_visibility(field_name, True)
        else:
            self.ui.more_info_button.setText("More info")
            self.ui.more_fields_button.hide()

            for field_name in self._active_fields:
                if field_name not in self._persistent_fields:
                    self.ui.current_version_card.set_field_visibility(field_name, False)

    def _selected_version_entities(self):
        """
        Returns a list of Version entities that are currently selected.
        """
        selection_model = self.ui.entity_version_view.selectionModel()
        indexes = selection_model.selectedIndexes()
        entities = []

        for i in indexes:
            entity = shotgun_model.get_sg_data(i)
            try:
                image_file = self.version_delegate.widget_cache[i].thumbnail.image_file_path
            except Exception:
                image_file = ""
            entity["__image_path"] = image_file
            entities.append(entity)

        return entities

    def _set_version_list_filter(self, filter_text):
        """
        Sets the Version list proxy model's filter pattern and forces
        a reselection of any items in the list.

        :param filter_text: The pattern to set as the proxy model's
                            filter wildcard.
        """
        # Forcing a reselection handles forcing a rebuild of any
        # editor widgets and will ensure we draw/sort/filter properly.
        self.version_proxy_model.setFilterWildcard(filter_text)
        self.version_delegate.force_reselection()

    def _setup_fields_menu(self):
        """
        Sets up the EntityFieldMenu and attaches it as the "More fields"
        button's menu.
        """
        entity = self.current_entity or {}
        menu = EntityFieldMenu(
            "Version",
            # project_id=entity.get("project", {}).get("id"),
        )
        menu.set_field_filter(self._field_filter)
        menu.set_checked_filter(self._checked_filter)
        menu.set_disabled_filter(self._disabled_filter)
        self._field_menu = menu
        self._field_menu.triggered.connect(self._field_menu_triggered)
        self.ui.more_fields_button.setMenu(menu)

    def _setup_version_list_fields_menu(self):
        """
        Sets up the EntityFieldMenu and attaches it as the "More fields"
        button's menu.
        """
        entity = self.current_entity or {}
        menu = EntityFieldMenu(
            "Version",
            # project_id=entity.get("project", {}).get("id"),
        )
        menu.set_field_filter(self._field_filter)
        menu.set_checked_filter(self._version_list_checked_filter)
        menu.set_disabled_filter(self._version_list_disabled_filter)
        self._version_list_field_menu = menu
        self._version_list_field_menu.triggered.connect(self._version_list_field_menu_triggered)
        self.ui.version_fields_button.setMenu(menu)

    def _setup_version_sort_by_menu(self):
        """
        Sets up the sort-by menu in the Versions tab.
        """
        entity = self.current_entity or {}
        self._version_sort_menu = QtGui.QMenu(self)
        self._version_sort_menu.setObjectName("version_sort_menu")

        ascending = QtGui.QAction("Sort Ascending", self)
        descending = QtGui.QAction("Sort Descending", self)
        ascending.setCheckable(True)
        descending.setCheckable(True)
        descending.setChecked(True)

        up_icon = QtGui.QIcon(":version_details/sort_up.png")
        up_icon.addPixmap(
            QtGui.QPixmap(":version_details/sort_up_on.png"),
            QtGui.QIcon.Active,
            QtGui.QIcon.On,
        )

        down_icon = QtGui.QIcon(":version_details/sort_down.png")
        down_icon.addPixmap(
            QtGui.QPixmap(":version_details/sort_down_on.png"),
            QtGui.QIcon.Active,
            QtGui.QIcon.On,
        )

        ascending.setIcon(up_icon)
        descending.setIcon(down_icon)

        self._version_sort_menu_directions = QtGui.QActionGroup(self)
        self._version_sort_menu_fields = QtGui.QActionGroup(self)
        self._version_sort_menu_directions.setExclusive(True)
        self._version_sort_menu_fields.setExclusive(True)

        self._version_sort_menu_directions.addAction(ascending)
        self._version_sort_menu_directions.addAction(descending)
        self._version_sort_menu.addActions([ascending, descending])
        self._version_sort_menu.addSeparator()

        for field_name in self._version_list_sort_by_fields:
            display_name = shotgun_globals.get_field_display_name(
                "Version",
                field_name,
                # project_id=entity.get("project", {}).get("id"),
            )

            action = QtGui.QAction(display_name, self)

            # We store the database field name on the action, but
            # display the "pretty" name for users.
            action.setData(field_name)
            action.setCheckable(True)
            action.setChecked((field_name == "id"))
            self._version_sort_menu_fields.addAction(action)
            self._version_sort_menu.addAction(action)

        self._version_sort_menu_directions.triggered.connect(self._toggle_sort_order)
        self._version_sort_menu_fields.triggered.connect(self._sort_version_list)
        self.ui.version_sort_button.setMenu(self._version_sort_menu)

    def _show_version_context_menu(self, point):
        """
        Shows the version list context menu containing all available
        actions. Which actions are enabled is determined by how many
        items in the list are selected.

        :param point:   The QPoint location to show the context menu at.
        """
        selection_model = self.ui.entity_version_view.selectionModel()
        versions = self._selected_version_entities()
        menu = SelectionContextMenu(versions)

        for menu_action in self._version_context_menu_actions:
            menu.addAction(action_definition=menu_action)

        # Show the menu at the mouse cursor. Whatever action is
        # chosen from the menu will have its callback executed.
        action = menu.exec_(self.ui.entity_version_view.mapToGlobal(point))
        menu.execute_callback(action)

    def _upload_file(self, sg, data):
        """
        Uploads any generic file attachments to Shotgun, parenting
        them to the given entity.

        :param sg:      A Shotgun API instance.
        :param data:    A dictionary containing "parent_entity_type",
                        "parent_entity_id", "file_path", and
                        "cleanup_after_upload" keys.
        """
        sg.upload(
            data["parent_entity_type"],
            data["parent_entity_id"],
            str(data["file_path"]),
        )

        if data.get("cleanup_after_upload", False):
            try:
                os.remove(data["file_path"])
            except Exception:
                pass

        self.ui.note_stream_widget.rescan(force_activity_stream_update=True)

    def __on_worker_signal(self, uid, request_type, data):
        """
        Run when a background task completes.

        :param uid:             The task ID that was completed.
        :param request_type:    The tasks type.
        :param data:            The data returned by the task's callable.
        """
        if uid == self._upload_uid:
            # TODO: Need to sort out why annotated attachments don't
            # show up in the activity stream until a new reply is
            # made AFTER the upload. This is not resolved by a relaunch
            # which makes me think that the sqlite db that the activity
            # stream is running off of is out of sync until it's forced
            # to refresh due to a new reply being created. <jbee>
            pass
        
    ##########################################################################
    # docking

    def _dock_location_changed(self):
        """
        Handles the dock being redocked in some location. This will
        trigger removing the default title bar.
        """
        self.parent().setTitleBarWidget(QtGui.QWidget(parent=self))

    def _hide_dock(self):
        """
        Hides the parent dock widget.
        """
        self.parent().hide()

    def _toggle_floating(self):
        """
        Toggles the parent dock widget's floating status.
        """
        if self.parent().isFloating():
            self.parent().setFloating(False)
            self._dock_location_changed()
        else:
            self.parent().setTitleBarWidget(None)
            self.parent().setFloating(True)

    ##########################################################################
    # version list actions

    def _toggle_sort_order(self):
        """
        Toggles ascending/descending sort ordering in the version list view.
        """
        self._sort_versions_ascending = not self._sort_versions_ascending
        self.version_proxy_model.sort(
            0, 
            (
                QtCore.Qt.AscendingOrder if 
                self._sort_versions_ascending else 
                QtCore.Qt.DescendingOrder
            ),
        )

        # We need to force a reselection after sorting. This will
        # remove edit widgets and allow a full repaint of the view,
        # and then reselect to go back to editing.
        self.version_delegate.force_reselection()

    def _sort_version_list(self, action=None):
        """
        Sorts the version list by the field chosen in the sort-by
        menu. This also triggers a reselection in the view in
        order to ensure proper sorting and drawing of items in the
        list.

        :param action:  The QAction chosen by the user from the menu.
        """
        if action:
            # The action group containing these actions is set to
            # exclusive activation, so we're always dealing with a
            # checked action when this slot is called. We can just
            # set the primary sort field, sort, and move on.
            field = action.data() or "id"
            self.version_proxy_model.primary_sort_field = field

        self.version_proxy_model.sort(
            0, 
            (
                QtCore.Qt.AscendingOrder if 
                self._sort_versions_ascending else 
                QtCore.Qt.DescendingOrder
            ),
        )

        # We need to force a reselection after sorting. This will
        # remove edit widgets and allow a full repaint of the view,
        # and then reselect to go back to editing.
        self.version_delegate.force_reselection()

    ##########################################################################
    # fields menu filters

    def _checked_filter(self, field):
        """
        Checked filter method for the EntityFieldMenu. Determines whether the
        given field should be checked in the field menu.

        :param field:   The field name being processed.
        """
        return (field in self._active_fields)

    def _version_list_checked_filter(self, field):
        """
        Checked filter method for the EntityFieldMenu. Determines whether the
        given field should be checked in the field menu.

        :param field:   The field name being processed.
        """
        return (field in self.version_delegate.fields)

    def _disabled_filter(self, field):
        """
        Disabled filter method for the EntityFieldMenu. Determines whether the
        given field should be active or disabled in the field menu.

        :param field:   The field name being processed.
        """
        return (field in self._persistent_fields)

    def _version_list_disabled_filter(self, field):
        """
        Disabled filter method for the EntityFieldMenu. Determines whether the
        given field should be active or disabled in the field menu.

        :param field:   The field name being processed.
        """
        return (field in self._version_list_persistent_fields)

    def _field_filter(self, field):
        """
        Field filter method for the EntityFieldMenu. Determines whether the
        given field should be included in the field menu.

        :param field:   The field name being processed.
        """
        # Allow any fields that we have a widget available for.
        return bool(
            self.ui.current_version_card.field_manager.supported_fields(
                "Version",
                [field],
            )
        )

