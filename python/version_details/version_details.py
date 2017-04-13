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
    ShotgunMenu,
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
    """
    QT Widget that displays details and Note thread data for a given Version
    entity.

    :signal entity_created(object): Fires when a Note or Reply entity is created by
            an underlying widget within the activity stream. Passes on a Shotgun
            entity definition in the form of a dict.
    :signal entity_loaded(object): Fires when a Version entity has been loaded by
            the widget. Passes on a Shotgun entity definition in the form of a dict.
    :signal note_selected(int): Fires when a Note entity is selected in the widget's
            note thread stream. Passes on the entity id of the selected note.
    :signal note_deselected(int): Fires when a Note entity is deselected. Passes on
            the entity id of the selected note.
    :signal note_arrived(int, object): Fires when a new Note entity arrives and is
            displayed in the widget's note thread stream. Passes on the entity id
            and Shotgun entity definition as an int and dict, respectively.
    :signal note_metadata_changed(int, str): Fires when the widget successfully
            updates a Note entity's metadata field. The Note entity's id and the
            new metadata are passed on.
    :signal note_attachment_arrived(int, str): Fires when an attachment file
            associated with a Note entity is successfully downloaded. The Note
            entity id and the path to the file on disk are passed on.
    """
    FIELDS_PREFS_KEY = "version_details_fields"
    ACTIVE_FIELDS_PREFS_KEY = "version_details_active_fields"
    VERSION_LIST_FIELDS_PREFS_KEY = "version_details_version_list_fields"
    NOTE_METADATA_FIELD = "sg_metadata"
    NOTE_MARKUP_PREFIX = "__note_markup__"

    # Emitted when an entity is created by the panel. The
    # entity type as a string and id as an int are passed
    # along.
    entity_created = QtCore.Signal(object)

    # Emitted when an entity is loaded in the panel.
    entity_loaded = QtCore.Signal(object)

    # The int is the id of the Note entity that was selected or deselected.
    note_selected = QtCore.Signal(int)
    note_deselected = QtCore.Signal(int)
    note_arrived = QtCore.Signal(int, object)
    note_metadata_changed = QtCore.Signal(int, str)
    note_attachment_arrived = QtCore.Signal(int, str)

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
        self._note_metadata_uids = []
        self._note_set_metadata_uids = []
        self._attachment_query_uids = {}
        self._attachment_uids = {}
        self._note_fields = [self.NOTE_METADATA_FIELD]
        self._attachments_filter = None
        self._dock_widget = None
        self._pre_submit_callback = None

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
            parent=self,
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
        self.ui.note_stream_widget.clickable_user_icons = False
        self.ui.note_stream_widget.show_note_links = False
        self.ui.note_stream_widget.highlight_new_arrivals = False
        self.ui.note_stream_widget.notes_are_selectable = True
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
        self._task_manager.task_completed.connect(self._on_task_completed)
        self.ui.note_stream_widget.note_selected.connect(self.note_selected.emit)
        self.ui.note_stream_widget.note_deselected.connect(self.note_deselected.emit)
        self.ui.note_stream_widget.note_arrived.connect(self._process_note_arrival)

        self._data_retriever.work_completed.connect(self.__on_worker_signal)
        self._data_retriever.work_failure.connect(self.__on_worker_failure)

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

        self.load_data(entity)
        self._load_stylesheet()
        self.show_title_bar_buttons(False)

        # This will handle showing or hiding the dock title bar
        # depending on what the parent is.
        self.setParent(parent)

    ##########################################################################
    # properties

    @property
    def current_entity(self):
        """
        The current Shotgun entity that is OR will become active in the widget.
        """
        return self._current_entity or self._requested_entity

    @property
    def is_pinned(self):
        """
        Returns True if the panel is pinned and not processing entity
        updates, and False if it is not pinned.
        """
        return self._pinned

    def _get_note_fields(self):
        """
        The list of Note entity field names that are queried and provided
        when note_arrived is emitted.

        :returns:   list(str, ...)
        """
        return self._note_fields

    def _set_note_fields(self, fields):
        self._note_fields = list(fields)

    note_fields = property(_get_note_fields, _set_note_fields)

    @property
    def note_threads(self):
        """
        The currently loaded Note threads keyed by Note entity id and
        containing a list of Shotgun entity dictionaries.

        Example structure containing a single Note entity::

            6038: [
                {
                    'content': 'This is a test note.',
                    'created_by': {
                        'id': 39,
                        'name': 'Jeff Beeland',
                        'type': 'HumanUser'
                    },
                    'id': 6038,
                    'sg_metadata': None,
                    'type': 'Note'
                }
            ]
        """
        return self.ui.note_stream_widget.note_threads

    def _get_attachments_filter(self):
        """
        If set to a compiled regular expression, attachment file names that match
        will be filtered OUT and NOT shown.
        """
        return self._attachments_filter

    def _set_attachments_filter(self, regex):
        self._attachments_filter = regex
        self.ui.note_stream_widget.attachments_filter = regex

    attachments_filter = property(
        _get_attachments_filter,
        _set_attachments_filter,
    )

    def _get_notes_are_selectable(self):
        """
        If True, note entity widgets in the activity stream will be selectable
        by the user.
        """
        return self.ui.note_stream_widget.notes_are_selectable

    def _set_notes_are_selectable(self, state):
        self.ui.note_stream_widget.notes_are_selectable = state

    notes_are_selectable = property(
        _get_notes_are_selectable,
        _set_notes_are_selectable,
    )

    def _get_pre_submit_callback(self):
        """
        The pre-submit callback function, if one is registered. If so, this
        Python callable will be run prior to Note or Reply submission, and
        will be given the calling :class:`NoteInputWidget` as its first and
        only argument.
        """
        return self.ui.note_stream_widget.pre_submit_callback

    def _set_pre_submit_callback(self, callback):
        self.ui.note_stream_widget.pre_submit_callback = callback

    pre_submit_callback = property(
        _get_pre_submit_callback,
        _set_pre_submit_callback,
    )

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
            self._data_retriever.execute_method(
                self.__upload_file,
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

        Action definitions passed in must take the following form::

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
        self.version_info_model.clear()
        self._requested_entity = None
        self._current_entity = None

    def select_note(self, note_id):
        """
        Select the note identified by the id. This will trigger a note_selected
        signal to be emitted
        """
        self.ui.note_stream_widget.select_note(note_id)

    def deselect_note(self):
        """
        If a note is currently selected, it will be deselected. This will NOT
        trigger a note_deselected signal to be emitted, as that is only emitted
        when the user triggers the deselection and not via procedural means.
        """
        self.ui.note_stream_widget.deselect_note()

    def download_note_attachments(self, note_id):
        """
        Triggers the attachments linked to the given Note entity to
        be downloaded.

        :param int note_id: The Note entity id.
        """
        # We're going to query the list of attachments live, because we don't
        # know if the cached data for the activity stream is up to date. The
        # reason that might be the case is that a new attachment doesn't
        # trigger a new activity event, so the cache doesn't know it's out
        # of date in that regard. It would be great to find a better solution
        # than not trusting the cache.
        attachment = self._data_retriever.execute_find(
            "Attachment",
            [[
                "attachment_links",
                "in",
                {"type":"Note", "id":note_id}
            ]],
            fields=[
                "this_file",
                "image",
                "attachment_links",
            ])
        self._attachment_query_uids[attachment] = note_id

    def get_note_attachments(self, note_id):
        """
        Gets the Attachment entities associated with the given Note
        entity.

        :param int note_id: The Note entity id.
        """
        return self.ui.note_stream_widget.get_note_attachments(note_id)

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
        if self._pinned and self._current_entity:
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

        for note_id in self.note_threads.keys():
            self._process_note_arrival(note_id)

        self.entity_loaded.emit(entity)

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

    def set_note_metadata(self, note_id, metadata):
        """
        Sets a Note entity's metadata in Shotgun.

        :param int note_id: The Note entity id.
        :param str metadata: The metadata to set in Shotgun.
        """
        self._note_set_metadata_uids.append(
            self._data_retriever.execute_update(
                "Note",
                note_id,
                {self.NOTE_METADATA_FIELD:metadata},
            )
        )

    def set_note_screenshot(self, image_path):
        """
        Takes the given file path to an image and sets the new note
        widget's thumbnail image.

        :param str image_path:  A file path to an image file on disk.
        """
        self.ui.note_stream_widget.note_widget._set_screenshot_pixmap(
            QtGui.QPixmap(image_path),
        )

    def set_pinned(self, checked):
        """
        Sets the "pinned" state of the details panel. When the panel is
        pinned it will not accept updates. It will, however, record the
        most recent entity passed to load_data that was not accepted. If
        the panel is unpinned at a later time, the most recent rejected
        entity update will be executed at that time.

        :param bool checked: True or False
        """
        self._pinned = checked

        if checked:
            self.ui.pin_button.setIcon(QtGui.QIcon(":/version_details/tack_hover.png"))
        else:
            self.ui.pin_button.setIcon(QtGui.QIcon(":/version_details/tack_up.png"))
            # If we have a valid _current_entity, be sure the incoming entity
            # has a different ID.
            if self._requested_entity and (not self._current_entity or (
                    self._requested_entity.get("id") != self._current_entity.get("id"))):
                self.load_data(self._requested_entity)

    def show_new_note_dialog(self, modal=True):
        """
        Shows a dialog that allows the user to input a new note.

        :param bool modal: Whether the dialog should be shown modally or not.
        """
        self.ui.note_stream_widget.show_new_note_dialog(modal=modal)

    def show_title_bar_buttons(self, state):
        """
        Sets the visibility of the undock and close buttons in the
        widget's title bar.

        :param bool state: Whether to show or hide the buttons.
        """
        self.ui.float_button.setVisible(state)
        self.ui.close_button.setVisible(state)

    def set_version_thumbnail(self, thumbnail_path, version_id=None):
        """
        Sets a Version entity's thumbnail image in Shotgun. If no Version
        id is provided, the current Version entity will be updated.

        :param str thumbnail_path: The path to the thumbnail file on disk.
        :param int version_id: The Version entity's id. If not provided
                               then the current Version entity loaded in
                               the widget will be used.
        """
        if not version_id and not self._current_entity:
            return

        version_id = version_id or self._current_entity["id"]
        self._data_retriever.execute_method(
            self.__upload_thumbnail,
            dict(
                entity_type="Version",
                entity_id=version_id,
                path=thumbnail_path,
            ),
        )

    def use_styled_title_bar(self, dock_widget):
        """
        If the use of the included, custom styled title bar is desired, the
        parent QDockWidget can be provided here and the styled title bar will
        be displayed.

        :param dock_widget: The parent QDockWidget.
        """
        self._dock_widget = dock_widget
        self.show_title_bar_buttons(True)
        dock_widget.dockLocationChanged.connect(self._dock_location_changed)

    ##########################################################################
    # internal utilities

    def _process_note_arrival(self, note_id):
        """
        When a new Note entity arrives from Shotgun in the version details
        widget, Dynamite is notified and provided the Note entity's metadata.

        :param int note_id: The id of the Note entity.
        """
        entity_fields = dict(
            Note=[self.NOTE_METADATA_FIELD],
            Reply=[self.NOTE_METADATA_FIELD], 
        )

        self._note_metadata_uids.append(
            self._data_retriever.execute_find_one(
                "Note",
                [["id", "is", note_id]],
                self.note_fields,
            )
        )

    def _on_task_completed(self):
        """
        Signaled whenever the worker completes something. This method will
        dispatch the work to different methods depending on what async task
        has completed.
        """
        self.ui.entity_version_view.repaint()
        self.ui.current_version_card.repaint()
        self.ui.note_stream_widget.repaint()

    def __on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something. This method will
        dispatch the work to different methods depending on what async task
        has completed.

        :param int uid: Unique id for the request.
        :param str request_type: The request class.
        :param dict data: The returned data.
        """
        if uid in self._note_metadata_uids:
            entity = data["sg"]
            self.note_arrived.emit(entity["id"], entity)
        elif uid in self._note_set_metadata_uids:
            entity = data["sg"]
            self.note_metadata_changed.emit(
                entity["id"],
                entity[self.NOTE_METADATA_FIELD],
            )
        elif uid in self._attachment_uids:
            note_id = self._attachment_uids[uid]
            del self._attachment_uids[uid]
            self.note_attachment_arrived.emit(note_id, data["file_path"])
        elif uid in self._attachment_query_uids:
            self._download_attachments(data["sg"], self._attachment_query_uids[uid])
            del self._attachment_query_uids[uid]

    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        
        :param int uid: Unique id for request that failed.
        :param str msg: The error message.
        """
        sgtk.platform.current_bundle().log_error(msg)

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

    def _download_attachments(self, attachments, note_id):
        """
        Downloads the contents of the given list of Attachment entities
        associated to a specific note entity.

        :param list attachments: A list of Attachment entities to download.
        :param int note_id: The id of the Note entity.
        """
        for attachment in attachments:
            attachment_uid = self._data_retriever.request_attachment(attachment)
            self._attachment_uids[attachment_uid] = note_id

    def _entity_created(self, entity):
        """
        Emits the entity_created signal.

        :param dict entity: The Shotgun entity dict that was created.
        """
        self.entity_created.emit(entity)

    def _field_menu_triggered(self, action):
        """
        Adds or removes a field when it checked or unchecked
        via the EntityFieldMenu.

        :param action: The QMenuAction that was triggered. 
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

        if not entity:
            return

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
        self._ensure_entity_project_schema_cached()
        self._setup_fields_menu()
        self._setup_version_list_fields_menu()
        self._setup_version_sort_by_menu()

    def _ensure_entity_project_schema_cached(self):
        """
        Ensures that the schema is cached before enabling the Fields buttons.

        This prevents errors when trying to display the field menu before the
        schema is properly cached.
        """

        # disconnect any previous connection so that the slot isn't called
        # multiple times
        try:
            shotgun_globals.schema_loaded.disconnect(self._on_schema_loaded)
        except Exception:
            pass

        # ---- disable the buttons until the schema is cached. set a tooltip
        #      just in case someone tries to click before the cache is loaded

        self.ui.more_fields_button.setEnabled(False)
        self.ui.more_fields_button.setToolTip("Caching SG fields. Please hold...")

        self.ui.version_fields_button.setEnabled(False)
        self.ui.version_fields_button.setToolTip("Caching SG fields. Please hold...")

        # use the current entity to retrieve the project id to ensure is cached
        entity = self._current_entity or {}
        project_id = entity.get("project", {}).get("id")

        # run this callback once the cache is loaded
        shotgun_globals.run_on_schema_loaded(
            self._on_schema_loaded, project_id=project_id)

    def _on_schema_loaded(self):
        """
        Callback that enables the field buttons once the schema is cached.
        """

        # disable these until the schema is cached
        self.ui.more_fields_button.setEnabled(True)
        self.ui.more_fields_button.setToolTip("Select fields to display")

        self.ui.version_fields_button.setEnabled(True)
        self.ui.version_fields_button.setToolTip("Select fields to display")

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

        :param bool checked: True or False
        """
        try:
            self.setUpdatesEnabled(False)

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
        finally:
            self.setUpdatesEnabled(True)

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
        entity = self._current_entity or {}
        menu = EntityFieldMenu(
            "Version",
            project_id=entity.get("project", {}).get("id"),
            parent=self,
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
        entity = self._current_entity or {}
        menu = EntityFieldMenu(
            "Version",
            project_id=entity.get("project", {}).get("id"),
            parent=self,
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
        self._version_sort_menu = ShotgunMenu(self)
        self._version_sort_menu.setObjectName("version_sort_menu")

        ascending = QtGui.QAction("Ascending", self)
        descending = QtGui.QAction("Descending", self)
        ascending.setCheckable(True)
        descending.setCheckable(True)
        descending.setChecked(True)

        self._version_sort_menu_directions = QtGui.QActionGroup(self)
        self._version_sort_menu_fields = QtGui.QActionGroup(self)
        self._version_sort_menu_directions.setExclusive(True)
        self._version_sort_menu_fields.setExclusive(True)

        self._version_sort_menu_directions.addAction(ascending)
        self._version_sort_menu_directions.addAction(descending)
        self._version_sort_menu.add_group([ascending, descending], title="Direction")

        field_actions = []

        for field_name in self._version_list_sort_by_fields:
            display_name = shotgun_globals.get_field_display_name(
                "Version",
                field_name,
            )

            action = QtGui.QAction(display_name, self)

            # We store the database field name on the action, but
            # display the "pretty" name for users.
            action.setData(field_name)
            action.setCheckable(True)
            action.setChecked((field_name == "id"))
            self._version_sort_menu_fields.addAction(action)
            field_actions.append(action)

        self._version_sort_menu.add_group(field_actions, title="By Field")
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

    def __upload_file(self, sg, data):
        """
        Uploads any generic file attachments to Shotgun, parenting
        them to the given entity.

        :param sg: A Shotgun API instance.
        :param dict data: A dictionary containing "parent_entity_type",
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

    def __upload_thumbnail(self, sg, data):
        """
        Uploads an image file as a thumbnail for the given entity. This
        is intended to be used with the execute_method call from a Shotgun
        data retriever object.

        The data dictionary will take the following form:
            dict(
                entity_type=str,
                entity_id=int,
                path=str,
            )

        :param sg: A Shotgun API instance.
        :param dict data: A dictionary of data passed through from the
                          Shotgun data retriever.
        """
        sg.upload_thumbnail(
            data["entity_type"],
            data["entity_id"],
            data["path"],
        )

        self.ui.note_stream_widget.rescan(force_activity_stream_update=True)
        self.ui.current_version_card.thumbnail.setPixmap(
            QtGui.QPixmap(data["path"])
        )
        
    ##########################################################################
    # docking

    def _dock_location_changed(self):
        """
        Handles the dock being redocked in some location. This will
        trigger removing the default title bar.
        """
        if self._dock_widget:
            self._dock_widget.setTitleBarWidget(QtGui.QWidget(parent=self))

    def _hide_dock(self):
        """
        Hides the parent dock widget.
        """
        if self._dock_widget:
            self._dock_widget.hide()

    def _toggle_floating(self):
        """
        Toggles the parent dock widget's floating status.
        """
        if self._dock_widget:
            if self._dock_widget.isFloating():
                self._dock_widget.setFloating(False)
                self._dock_location_changed()
            else:
                self._dock_widget.setTitleBarWidget(None)
                self._dock_widget.setFloating(True)

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

        :param str field: The field name being processed.
        """

        # see if we can display this field
        supported = self.ui.current_version_card.field_manager.supported_fields(
            "Version", [field])

        if field not in supported:
            return False

        # get the current version entity's project id
        entity = self._current_entity or {}
        project_id = entity.get("project", {}).get("id")

        # Detect bubble fields. If the field_name is "sg_sequence.Sequence.code"
        # then we know we want to get the data type of the "code" field on the
        # "Sequence" entity type.
        if "." in field:
            (entity_type, field_name) = field.split(".")[-2:]
        else:
            (entity_type, field_name) = ("Version", field)

        # make sure the field is visible
        if not shotgun_globals.field_is_visible(
                entity_type, field_name, project_id=project_id):
            return False

        return True

