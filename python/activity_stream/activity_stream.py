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
import sys
import sgtk

from sgtk.platform.qt import QtCore, QtGui

from .ui.activity_stream_widget import Ui_ActivityStreamWidget

from .widget_new_item import NewItemWidget, SimpleNewItemWidget
from .widget_note import NoteWidget
from .widget_value_update import ValueUpdateWidget
from .dialog_reply import ReplyDialog
from .data_manager import ActivityStreamDataHandler
from .overlaywidget import SmallOverlayWidget

note_input_widget = sgtk.platform.current_bundle().import_module("note_input_widget")

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
utils = sgtk.platform.import_framework("tk-framework-shotgunutils", "utils")

class ActivityStreamWidget(QtGui.QWidget):
    """
    QT Widget that displays the Shotgun activity stream for an entity.
    
    :signal entity_requested(str, int): Fires when someone clicks an entity inside
            the activity stream. The returned parameters are entity type and entity id.
    :signal playback_requested(dict): Fires when someone clicks the playback url
            on a version. Returns a shotgun dictionary with information
            about the version.
    :signal entity_created(object): Fires when a Note or Reply entity is created by
            an underlying widget within the activity stream. Returns a Shotgun dictionary
            with information about the new Entity.
    :ivar reply_dialog: When a ReplyDialog is active it can be accessed here. If there
                        is no ReplyDialog active, then this will be set to None.
    :vartype reply_dialog: .dialog_reply.ReplyDialog or None
    """
    # max number of items to show in the activity stream.
    MAX_STREAM_LENGTH = 20

    # Activity attributes that we do not want displayed.
    _SKIP_ACTIVITY_ATTRIBUTES = ["viewed_by_current_user"]

    entity_requested = QtCore.Signal(str, int)
    playback_requested = QtCore.Signal(dict)

    # The int is the Note entity id that was selected or deselected.
    note_selected = QtCore.Signal(int)
    note_deselected = QtCore.Signal(int)
    note_arrived = QtCore.Signal(int)

    # Emitted when a Note or Reply entity is created. The
    # entity type as a string and id as an int will be
    # provided.
    #
    # dict(entity_type="Note", id=1234)
    entity_created = QtCore.Signal(object)

    def __init__(self, parent):
        """
        :param parent: QT parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        self._bundle = sgtk.platform.current_bundle()
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ActivityStreamWidget() 
        self.ui.setupUi(self)

        # The note widget will be turned on when an entity is loaded
        # if the entity is of an appropriate type.
        self.ui.note_widget.hide()

        # customizations
        self._allow_screenshots = True
        self._show_sg_stream_button = True
        self._version_items_playable = True
        self._clickable_user_icons = True
        self._show_note_links = True
        self._highlight_new_arrivals = True
        self._notes_are_selectable = False
        self._attachments_filter = None
        
        # apply styling
        self._load_stylesheet()

        # keep an overlay for loading
        overlay_module = self._bundle.import_module("overlay_widget")
        self.__overlay = overlay_module.ShotgunOverlayWidget(self)
        self.__small_overlay = SmallOverlayWidget(self)

        # set insertion order into list to be bottom-up
        self.ui.activity_stream_layout.setDirection(QtGui.QBoxLayout.BottomToTop)

        # create a data manager to handle backend
        self._data_manager = ActivityStreamDataHandler(self)

        # set up signals
        self._data_manager.note_arrived.connect(self._process_new_note)
        self._data_manager.update_arrived.connect(self._process_new_data)
        self._data_manager.thumbnail_arrived.connect(self._process_thumbnail)
        self._data_manager.requesting_ui_refresh.connect(self._clear)
        self.ui.note_widget.entity_created.connect(self._on_entity_created)
        self.ui.note_widget.data_updated.connect(self.rescan)
        
        # keep handles to all widgets to be nice to the GC
        self._loading_widget = None
        self._activity_stream_static_widgets = []
        self._activity_stream_data_widgets = {}
                
        # state management
        self._task_manager = None
        self._sg_entity_dict = None
        self._entity_type = None
        self._entity_id = None
        self._select_on_arrival = dict()

        # We'll be keeping a persistent reply dialog available because
        # we need to connect to a signal that it's emitting. It's easiest
        # to do that if we're dealing with an object that persists.
        self.reply_dialog = ReplyDialog(
            self,
            self._task_manager,
            note_id=None,
            allow_screenshots=self._allow_screenshots,
        )

        # We'll allow for a pre-note-creation callback. This is for additional
        # pre-processing that needs to occur before a Note or Reply is created
        # in Shotgun. This makes sure that the activity stream data coming down
        # during the rescan after submission contains anything like additional
        # attachments that this widget didn't explicitly handle itself prior to
        # submission.
        self._pre_submit_callback = None
        self.reply_dialog.note_widget.entity_created.connect(self._on_entity_created)

    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.
        
        :param task_manager: Background task manager to use
        :type task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager` 
        """
        self._task_manager = task_manager
        shotgun_globals.register_bg_task_manager(task_manager)
        self._data_manager.set_bg_task_manager(task_manager)
        self.ui.note_widget.set_bg_task_manager(task_manager)
        self.reply_dialog.set_bg_task_manager(task_manager)
        
    def destroy(self):
        """
        Should be called before the widget is closed
        """
        self._data_manager.destroy()
        self._task_manager = None

    ############################################################################
    # properties

    @property
    def note_threads(self):
        """
        The currently loaded note threads, keyed by Note entity id and
        containing a list of Shotgun entity dictionaries. All note threads
        currently displayed by the activity stream widget will be returned.

        Example structure containing a Note, a Reply, and an attachment::

            6040: [
                {
                    'addressings_cc': [],
                    'addressings_to': [],
                    'client_note': False,
                    'content': 'This is a test note.',
                    'created_at': 1466477744.0,
                    'created_by': {
                        'id': 39,
                        'name': 'Jeff Beeland',
                        'type': 'HumanUser'
                    },
                    'id': 6040,
                    'note_links': [
                        {
                            'id': 1167,
                            'name': '123',
                            'type': 'Shot'
                        },
                        {
                            'id': 6023,
                            'name': 'Scene_v030_123',
                            'type': 'Version'
                        }
                    ],
                    'read_by_current_user': 'read',
                    'subject': "Jeff's Note on Scene_v030_123, 123",
                    'tasks': [
                        {
                            'id': 2118,
                            'name': 'Comp',
                            'type': 'Task'
                        }
                    ],
                    'type': 'Note',
                    'user': {
                        'id': 39,
                        'name': 'Jeff Beeland',
                        'type': 'HumanUser'
                    },
                    'user.ApiUser.image': None,
                    'user.ClientUser.image': None,
                    'user.HumanUser.image': 'https://url_to_file'
                },
                {
                    'content': 'test reply',
                    'created_at': 1469221928.0,
                    'id': 23,
                    'type': 'Reply',
                    'user': {
                        'id': 39,
                        'image': 'https://url_to_file',
                        'name': 'Jeff Beeland',
                        'type': 'HumanUser'
                    }
                },
                {
                    'attachment_links': [
                        {
                            'id': 6051,
                            'name': "Jeff's Note on Scene_v030_123, 123 - testing.",
                            'type': 'Note'
                        }
                    ],
                    'created_at': 1469484693.0,
                    'created_by': {
                        'id': 39,
                        'name': 'Jeff Beeland',
                        'type': 'HumanUser'
                    },
                    'id': 601,
                    'image': 'https://url_to_file',
                    'this_file': {
                        'content_type': 'image/png',
                        'id': 601,
                        'link_type': 'upload',
                        'name': 'screencapture_vrviim.png',
                        'type': 'Attachment',
                        'url': 'https://url_to_file'
                    },
                    'type': 'Attachment'
                },
            ]

        """
        return self._data_manager.note_threads

    @property
    def note_widget(self):
        """
        Returns the :class:`~note_input_widget.NoteInputWidget` contained within
        the ActivityStreamWidget. Note that this is the widget used for NEW note
        input and not Note replies. To get the NoteInputWidget used for Note
        replies, access can be found via :meth:`ReplyDialog.note_widget`.
        """
        return self.ui.note_widget

    def _get_clickable_user_icons(self):
        """
        Whether user icons in the activity stream display as clickable.
        If True, a pointing hand cursor will be shown when the mouse is
        hovered over the icons, otherwise the default arrow cursor will be
        used.
        """
        return self._clickable_user_icons

    def _set_clickable_user_icons(self, state):
        self._clickable_user_icons = bool(state)

        for widget in self._activity_stream_data_widgets.values():
            if isinstance(widget, NoteWidget):
                if state:
                    widget.set_user_thumb_cursor(QtCore.Qt.PointingHandCursor)
                else:
                    widget.set_user_thumb_cursor(QtCore.Qt.ArrowCursor)

    clickable_user_icons = property(
        _get_clickable_user_icons,
        _set_clickable_user_icons,
    )

    def _get_pre_submit_callback(self):
        """
        The pre-submit callback. This is None if one is not set, or a Python
        callable if it is. This callable is run prior to submission of a new
        Note or Reply. Note that the first (and only) argument passed to the
        callback will be the calling :class:`NoteInputWidget`.

        :returns:   Python callable or None
        """
        return self._pre_submit_callback

    def _set_pre_submit_callback(self, callback):
        self._pre_submit_callback = callback
        self.reply_dialog.note_widget.pre_submit_callback = callback
        self.note_widget.pre_submit_callback = callback

    pre_submit_callback = property(
        _get_pre_submit_callback,
        _set_pre_submit_callback,
    )

    def _get_allow_screenshots(self):
        """
        Whether this activity stream is allowed to give the user access to a
        button that performs screenshot operations.
        """
        return self._allow_screenshots

    def _set_allow_screenshots(self, state):
        self._allow_screenshots = bool(state)
        self.ui.note_widget.allow_screenshots(self._allow_screenshots)

    allow_screenshots = property(
        _get_allow_screenshots,
        _set_allow_screenshots,
    )

    def _get_show_sg_stream_button(self):
        """
        Whether the button to navigate to Shotgun is shown in the stream.
        """
        return self._show_sg_stream_button

    def _set_show_sg_stream_button(self, state):
        """
        Sets whether to show the button to navigate to Shotgun.

        :param state: True or False
        """
        self._show_sg_stream_button = bool(state)

    show_sg_stream_button = property(
        _get_show_sg_stream_button,
        _set_show_sg_stream_button,
    )

    def _get_version_items_playable(self):
        """
        Whether the label representing a created Version entity is shown
        as being "playable" within the UI. If True, then a play icon is
        visible over the thumbnail image, and no icon overlay is shown
        when False.
        """
        return self._version_items_playable

    def _set_version_items_playable(self, state):
        self._version_items_playable = bool(state)

    version_items_playable = property(
        _get_version_items_playable,
        _set_version_items_playable,
    )

    def _get_show_note_links(self):
        """
        If True, lists out the parent entity as a list of clickable
        items for each Note entity that is represented in the activity
        stream.
        """
        return self._show_note_links

    def _set_show_note_links(self, state):
        self._show_note_links = bool(state)

    show_note_links = property(
        _get_show_note_links,
        _set_show_note_links,
    )

    def _get_highlight_new_arrivals(self):
        """
        If True, highlights items in the activity stream that are new
        since the last time data was loaded.
        """
        return self._highlight_new_arrivals

    def _set_highlight_new_arrivals(self, state):
        self._highlight_new_arrivals = bool(state)

    highlight_new_arrivals = property(
        _get_highlight_new_arrivals,
        _set_highlight_new_arrivals,
    )

    def _get_notes_are_selectable(self):
        return self._notes_are_selectable

    def _set_notes_are_selectable(self, state):
        self._notes_are_selectable = bool(state)

    notes_are_selectable = property(
        _get_notes_are_selectable,
        _set_notes_are_selectable,
    )

    def _get_attachments_filter(self):
        """
        If set to a compiled regular expression, attachment file names that match
        will be filtered OUT and NOT shown.

        .. note:: An re.match() is used, which means the regular expression must
                  match from the start of the attachment file's basename. See Python's
                  "re" module documentation for Python 2.x for more information and
                  examples.

        Example to match only ".gif" extensions::

            re.compile(r"\w+[.]gif$")
        """
        return self._attachments_filter

    def _set_attachments_filter(self, regex):
        self._attachments_filter = regex

    attachments_filter = property(_get_attachments_filter, _set_attachments_filter)
        
    ############################################################################
    # public interface

    def select_note(self, note_id):
        selectedWidget = None
        for widget in self._activity_stream_data_widgets.values():
            if isinstance(widget, NoteWidget):
                match = widget.note_id == note_id
                if match and not widget.selected:
                    self._note_selected_changed(True, widget.note_id)
                    selectedWidget = widget
                widget.set_selected(match)
        if selectedWidget is not None:
            self.ui.activity_stream_scroll_area.ensureWidgetVisible(selectedWidget)

    def deselect_note(self):
        """
        If a note is currently selected, it will be deselected. This will NOT
        trigger a note_deselected signal to be emitted, as that is only emitted
        when the user triggers the deselection and not via procedural means.
        """
        for widget in self._activity_stream_data_widgets.values():
            if isinstance(widget, NoteWidget) and widget.selected:
                widget.set_selected(False)
                # We only support single selection right now, so we don't
                # need to continue on once we've hit a note that's selected.
                return

    def get_note_attachments(self, note_id):
        """
        Gets the Attachment entities associated with the given Note
        entity. Only attachments from Notes currently loaded by the
        activity stream widget will be returned.

        .. note:: It is possible for attachments to be added to a Note
                  entity after the activity stream data has been cached.
                  In this situation, those attachments will NOT be returned,
                  as Shotgun will not be requeried for that new data unless
                  specifically requested to do so.

        :param int note_id: The Note entity id.
        """
        for widget in self._activity_stream_data_widgets.values():
            if isinstance(widget, NoteWidget) and widget.note_id == note_id:
                return widget.attachments
        
    def load_data(self, sg_entity_dict):
        """
        Reset the state of the widget and then load up the data
        for a given entity.
        
        :param dict sg_entity_dict: Dictionary with keys type and id
        """
 
        self._bundle.log_debug("Setting up activity stream for entity %s" % sg_entity_dict)
        # clean up everything first
        self._clear()
        
        # change the state
        self._sg_entity_dict = sg_entity_dict
        self._entity_type = self._sg_entity_dict["type"]
        self._entity_id = self._sg_entity_dict["id"]
        
        # tell our "new note" widget which entity it should link up against 
        self.ui.note_widget.set_current_entity(self._entity_type, 
                                               self._entity_id)

        # to mimic the behavior in shotgun - which seems quite strange and
        # inconsistent for users, we need to disable to note dialog for 
        # these cases

        # note - this may return [] if shotgun globals aren't yet cached
        schema_fields = shotgun_globals.get_entity_fields(self._entity_type)
        is_non_project_entity_type = len(schema_fields) > 0 and "project" not in schema_fields

        # if the project context is None, the entity is a non project entity and it's NOT
        # the project entity itself, we don't have access to any project state.
        no_project_available = (
            self._bundle.context.project is None and
            is_non_project_entity_type and
            self._entity_type != "Project"
        )

        # also disable note creation in the case we have a site context
        # and a non-project entity
        if self._entity_type in ["ApiUser", "HumanUser", "ClientUser"]:
            self.ui.note_widget.setVisible(False)
        elif no_project_available:
            # we don't have any project to hang these notes off, so disable
            # the note integration
            self.ui.note_widget.setVisible(False)
        else:
            self.ui.note_widget.setVisible(True)

        # now load cached data for the given entity
        self._bundle.log_debug("Setting up db manager....")
        ids_to_process = self._data_manager.load_activity_data(self._entity_type, 
                                                               self._entity_id,
                                                               self.MAX_STREAM_LENGTH)

        if len(ids_to_process) == 0:
            # nothing cached - show spinner!
            # NOTE!!!! - cannot use the actual spinning animation because
            # this triggers the GIL bug where signals from threads
            # will deadlock the GIL
            self.__overlay.show_message("Loading Shotgun Data...")

        all_reply_users = []
        attachment_requests = []
        
        ###############################################################
        # Phase 1 - render the UI.
        
        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes
        self._bundle.log_debug("Start building widgets based on cached data...")
        self.setVisible(False)
        try:

            # we are building the widgets bottom up.
            # first of all, insert a widget that will expand so that 
            # it consumes all unused space. This is to keep other
            # widgets from growing when there are only a few widgets
            # available in the scroll area.
            self._bundle.log_debug("Adding expanding base widget...")            
            
            expanding_widget = QtGui.QLabel(self)
            self.ui.activity_stream_layout.addWidget(expanding_widget)
            self.ui.activity_stream_layout.setStretchFactor(expanding_widget, 1)
            self._activity_stream_static_widgets.append(expanding_widget)

            if self.show_sg_stream_button:
                sg_stream_button = QtGui.QPushButton(self)
                sg_stream_button.setText("Click here to see the Activity stream in Shotgun.")
                sg_stream_button.setObjectName("full_shotgun_stream_button")
                sg_stream_button.setCursor(QtCore.Qt.PointingHandCursor)
                sg_stream_button.setFocusPolicy(QtCore.Qt.NoFocus)
                sg_stream_button.clicked.connect(self._load_shotgun_activity_stream)
                
                self.ui.activity_stream_layout.addWidget(sg_stream_button)
                self._activity_stream_static_widgets.append(sg_stream_button)
    
            # ids are returned in async order. Now pop them onto the activity stream,
            # old items first order...
            self._bundle.log_debug("Adding activity widgets...")
            for activity_id in ids_to_process:
                w = self._create_activity_widget(activity_id)
                # note that not all activity data entries generate
                # a widget in our factory method.      
                if w:
                    # a widget was generated! Insert it into
                    # the widget layouts etc.
                    self._activity_stream_data_widgets[activity_id] = w
                    self.ui.activity_stream_layout.addWidget(w)        
            
                    # run extra init for notes
                    # this is to fetch the actual note payload - 
                    # content, replies, attachments etc.
                    if isinstance(w, NoteWidget):
                        data = self._data_manager.get_activity_data(activity_id)
                        note_id = data["primary_entity"]["id"]
                        (note_reply_users, note_attachment_requests) = self._populate_note_widget(w, activity_id, note_id)
                        # extend user and attachment requests to our full list
                        # so that we can request thumbnails for these later...
                        all_reply_users.extend(note_reply_users)                    
                        attachment_requests.extend(note_attachment_requests)
            
            # last, create "loading" widget
            # to put at the top of the list.
            #
            # We add this into the scroll area so that it scrolls with the
            # rest of the items in the list.
            #
            self._loading_widget = QtGui.QLabel(self)
            self._loading_widget.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
            self._loading_widget.setText("Loading data from Shotgun...") 
            self._loading_widget.setObjectName("loading_widget")
            self.ui.activity_stream_layout.addWidget(self._loading_widget)
        
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            self._bundle.log_debug("...UI building complete!")
                
        ###############################################################
        # Phase 2 - request additional data.
        # note that we don't interleave these requests with building
        # the ui - this is to minimise the risk of GIL signal issues
                
        # request thumbs
        self._bundle.log_debug("Request thumbnails...")
        for activity_id in ids_to_process:
            self._data_manager.request_activity_thumbnails(activity_id)
        
        for attachment_req in attachment_requests:
            self._data_manager.request_attachment_thumbnail(attachment_req["activity_id"], 
                                                            attachment_req["attachment_group_id"], 
                                                            attachment_req["attachment_data"])
        
        # now request thumbnails for all users who have replied, but 
        # only once per user
        reply_users_dup_check = []
        for reply_user in all_reply_users:
            
            unique_user = (reply_user["type"], reply_user["id"]) 
            
            if unique_user not in reply_users_dup_check: 
                reply_users_dup_check.append(unique_user)
                self._data_manager.request_user_thumbnail(reply_user["type"], 
                                                          reply_user["id"],
                                                          reply_user["image"])
        
        self._bundle.log_debug("...done")
        
        # and now request an update check
        self._bundle.log_debug("Ask db manager to ask shotgun for updates...")
        self._data_manager.rescan()
        self._bundle.log_debug("...done")

    def show_new_note_dialog(self, modal=True):
        """
        Shows a dialog that allows the user to input a new note.

        .. note:: The return value of the new note dialog is not provided,
                  as the activity stream widget will emit an entity_created
                  signal if the user successfully creates a new Note entity.

        :param bool modal: Whether the dialog should be shown modally or not.
        """
        if self._entity_id == None:
            self._bundle.log_debug("Skipping New Note Dialog - No entity loaded.")
            return

        note_dialog = note_input_widget.NoteInputDialog(parent=self)
        note_dialog.entity_created.connect(self._on_entity_created)
        note_dialog.data_updated.connect(self.rescan)
        note_dialog.set_bg_task_manager(self._task_manager)
        note_dialog.set_current_entity(self._entity_type, self._entity_id)

        if modal:
            note_dialog.exec_()
        else:
            note_dialog.show()


    def rescan(self, force_activity_stream_update=False):
        """
        Triggers a rescan of the current activity stream data.

        :param force_activity_stream_update:    If True, will force a requery
                                                of activity stream data, even
                                                if it is already cached.
        :type force_activity_stream_update:     bool
        """
        # kick the data manager to rescan for changes
        self._data_manager.rescan(
            force_activity_stream_update=force_activity_stream_update,
        )
            
    ############################################################################
    # internals

    def _load_stylesheet(self):
        """
        Loads in a stylesheet from disk
        """
        qss_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.qss")
        try:
            f = open(qss_file, "rt")
            qss_data = f.read()
            # apply to widget (and all its children)
            self.setStyleSheet(qss_data)
        finally:
            f.close()
        
    def _clear(self):
        """
        Clear the widget. This will remove all items the UI
        """
        is_qt4 = QtCore.__version__.startswith("4.")

        self._bundle.log_debug("Clearing UI...")
        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes
        #
        # NOTE: For some reason this causes a crash when in a PySide2
        # environment. We'll only do it if we're in Qt4 as a result.
        if is_qt4:   
            self.setVisible(False)
        
        # scroll to top
        self.ui.activity_stream_scroll_area.verticalScrollBar().setValue(0)
        
        try:
            self._bundle.log_debug("Clear loading widget")
            self._clear_loading_widget()

            self._bundle.log_debug("Removing all widget items")
            for x in self._activity_stream_data_widgets.values():
                # remove widget from layout:
                self.ui.activity_stream_layout.removeWidget(x)
                # set it's parent to None so that it is removed from the widget hierarchy
                x.setParent(None)
                utils.safe_delete_later(x)
        
            self._bundle.log_debug("Clearing python data structures")
            self._activity_stream_data_widgets = {}
    
            self._bundle.log_debug("Removing expanding widget")
            for w in self._activity_stream_static_widgets:
                self.ui.activity_stream_layout.removeWidget(w)
                w.setParent(None)
                utils.safe_delete_later(w)

            self._activity_stream_static_widgets = []
        
        finally:
            # make the window visible again and trigger a redraw
            #
            # NOTE: For some reason this causes a crash when in a PySide2
            # environment. We'll only do it if we're in Qt4 as a result.
            if is_qt4:
                self.setVisible(True)

            # Since we have no entity loaded, we don't need to show
            # the note widget.
            self.ui.note_widget.setVisible(False)

            self.ui.note_widget.clear()
            
    def _clear_loading_widget(self):
        """
        Remove the loading widget from the widget list
        """
        if self._loading_widget:
            self._bundle.log_debug("Clearing the loading widget")
            self.ui.activity_stream_layout.removeWidget(self._loading_widget)
            self._loading_widget.setParent(None)
            utils.safe_delete_later(self._loading_widget)
            self._loading_widget = None
            self._bundle.log_debug("...done")
        
    def _populate_note_widget(self, note_widget, activity_id, note_id):
        """
        Load note content and replies into a note widget
        
        :param note_widget: Note widget to populate with replies and
                            attachments.
        :param activity_id: Activity stream id to load
        :param note_id: Note id to load
        
        :returns: (reply_users, attachment_requests) where reply_users is a 
                  list of users (dict with type, id, name and image) for each 
                  of the replies and attachment_requests a list of dicts of 
                  attahchment request dictionaries
        """
        # set note content            
        note_thread_data = self._data_manager.get_note(note_id)
        
        attachment_requests = []
        reply_users = []
        
        if note_thread_data:
            # we have cached note data
            note_data = note_thread_data[0]
            replies_and_attachments = note_thread_data[1:] 
            
            # set up the note data first
            note_widget.set_note_info(note_data)
            
            # now add replies
            note_widget.add_replies(replies_and_attachments)
            
            # add a reply button and connect it
            reply_button = note_widget.add_reply_button()
            reply_button.clicked.connect(lambda : self._on_reply_clicked(note_id))

            # get list of users who have replied
            for item in replies_and_attachments:
                if item["type"] == "Reply":
                    # note that the reply data structure is special:
                    # the 'user' key is not a normal sg link dict, 
                    # but contains an additional image field to describe
                    # the thumbnail:
                    # 
                    # {'content': 'Reply content...', 
                    #  'created_at': 1438649419.0, 
                    #  'type': 'Reply', 
                    #  'id': 73, 
                    #  'user': {'image': '...', 
                    #           'type': 'HumanUser', 
                    #           'id': 38, 
                    #           'name': 'Manne Ohrstrom'}}]
                    reply_users.append(item["user"])
            
            # get all attachment data
            # can request thumbnails post UI build
            for attachment_group_id in note_widget.get_attachment_group_widget_ids():
                agw = note_widget.get_attachment_group_widget(attachment_group_id)
                for attachment_data in agw.get_data():                        
                    ag_request = {"attachment_group_id": attachment_group_id,
                                  "activity_id": activity_id,
                                  "attachment_data": attachment_data}
                    attachment_requests.append(ag_request)
            
        return (reply_users, attachment_requests)
        
        
    def _create_activity_widget(self, activity_id):
        """
        Create a widget for a given activity id
        If the activity id is not supported by the implementation, 
        returns None. This can for example happen if the type of
        data returned by the activity stream doesn't have a 
        suitable widget implemented.

        :returns: Activity widget object or None
        """
        data = self._data_manager.get_activity_data(activity_id)
        
        widget = None
        
        # factory logic
        if data["update_type"] == "create":
            
            if data["primary_entity"]["type"] in ["Version", "PublishedFile", "TankPublishedFile"]:
                # full on 'new item' widget with thumbnail, description etc.
                widget = NewItemWidget(self)
                widget.interactive = self.version_items_playable
            
            elif data["primary_entity"]["type"] == "Note":
                # new note
                widget = NoteWidget(data["primary_entity"]["id"], self)
                widget.show_note_links = self.show_note_links
                widget.attachments_filter = self.attachments_filter

                # If it's been requested that we select this Note entity's widget when it's
                # constructed, then we do so here. This is the situation where the user has
                # created a new Note, which upon completion we want to have autoselected.
                if data["primary_entity"]["id"] == self._select_on_arrival.get("id"):
                    # First we need to deselect whatever is selected, because we're going
                    # to be selecting our new widget right after.
                    for w in self._activity_stream_data_widgets.values():
                        if isinstance(w, NoteWidget):
                            if w.selected:
                                w.set_selected(False)
                                self._note_selected_changed(False, w.note_id)

                    widget.set_selected(True)
                    self._note_selected_changed(True, widget.note_id)
                    self._select_on_arrival = dict()

            else:
                # minimalistic 'new' widget for all other cases
                widget = SimpleNewItemWidget(self)
                            
        elif data["update_type"] == "create_reply":
            # new note widget
            widget = NoteWidget(data["primary_entity"]["id"], self)
            widget.show_note_links = self.show_note_links
            widget.attachments_filter = self.attachments_filter
            
        elif data["update_type"] == "update":
            # 37660: We're going to ignore "viewed by" activity for the time being.
            # According to the review team these entries shouldn't have been returned
            # as part of the stream anyway, but we have existing data that might
            # contain these entries that we need to handle elegantly.
            if data.get("meta", {}).get("attribute_name") not in self._SKIP_ACTIVITY_ATTRIBUTES:
                widget = ValueUpdateWidget(self)
            
        else:
            self._bundle.log_debug("Activity type not supported and will not be "
                                "rendered: %s" % data["update_type"])
        
        # initialize the widget
        if widget:
            widget.set_host_entity(self._entity_type, self._entity_id)
            widget.set_info(data)
            widget.entity_requested.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))
            widget.playback_requested.connect(lambda sg_data: self.playback_requested.emit(sg_data))

        # If we're not wanting the user icons to display as clickable, then
        # we need to set their cursor to be the default arrow cursor. Otherwise
        # we don't need to do anything because they default to the clickable
        # finger-pointing cursor.
        if not self.clickable_user_icons and isinstance(widget, NoteWidget):
            widget.set_user_thumb_cursor(QtCore.Qt.ArrowCursor)
                    
        return widget

    def _note_selected_changed(self, selected, note_id):
        """
        Handles a change in selection state for a given Note entity id.

        :param bool selected: The new selection state of the Note.
        :param int note_id: The Note entity id.
        """
        if selected:
            self.note_selected.emit(note_id)
        else:
            self.note_deselected.emit(note_id)
        
    def _process_new_data(self, activity_ids):
        """
        Process new activity ids as they arrive from
        the data manager.
        
        :param activity_ids: List of activity ids
        """
        self._bundle.log_debug(
            "Process new data called for %s activity events" % len(activity_ids)
        )

        # keep track of new note widgets created
        note_widgets_added = []

        # remove the "loading please wait .... widget
        self._clear_loading_widget()
        
        
        # note! For an item which hasn't been previously been cached or
        # hasn't been visited for some time, there may be a lot more than
        # MAX_STREAM_LENGTH updates. In this case, truncate the stream.
        # this will result in a UI where you may have a maxmimum of 
        # MAX_STREAM_LENGTH * 2 items (already loaded + new) and there
        # may be gaps in activity data because we always want to show
        # the latest data, so when we cull, it happens in the 'middle'
        # of the stream, resulting in existing data, the a potential gap
        # and then MAX_STREAM_LENGTH items.
        #
        # Note that this is in the UI only, so a refresh of the page 
        # would immediately rectify the discrepancy.  
        
        # load in the new data
        # the list of ids is delivered in ascending order
        # and we pop them on to the widget

        if len(activity_ids) > self.MAX_STREAM_LENGTH:
            self._bundle.log_debug("Capping the %s new activity items down to "
                                "%s items" % (len(activity_ids), self.MAX_STREAM_LENGTH))
        
            # transform [10,11,12,13,14,15,16,17] -> [15,16,17]
            activity_ids = activity_ids[-self.MAX_STREAM_LENGTH:]
        
        for activity_id in activity_ids:
            self._bundle.log_debug("Creating new widget...")
            w = self._create_activity_widget(activity_id)
            if w:            
                self._activity_stream_data_widgets[activity_id] = w
                self._bundle.log_debug("Adding %s to layout" % w)
                self.ui.activity_stream_layout.addWidget(w)        
                # add special blue border to indicate that this is a new arrival
                if self.highlight_new_arrivals:
                    w.setStyleSheet("QFrame#frame{ border: 1px solid rgba(48, 167, 227, 50%); }")
                # register if it is a note so we can post process
                if isinstance(w, NoteWidget):
                    note_widgets_added.append(w)
        
        # when everything is loaded in, load the thumbs
        self._bundle.log_debug("Requesting thumbnails")
        for activity_id in activity_ids:
            self._data_manager.request_activity_thumbnails(activity_id)
                
        self._bundle.log_debug("Process new data complete.")

        # now cull out any activity items that are duplicated in the list
        # this may be the case if a note has been replied to - in this case
        # the note already exists in the list
        note_ids_added = [widget.note_id for widget in note_widgets_added]
        for widget in self._activity_stream_data_widgets.values():
            if isinstance(widget, NoteWidget) and widget not in note_widgets_added:
                if widget.note_id in note_ids_added:
                    widget.hide()

        # turn off the overlay in case it is spinning
        # (which only happens on a full load)
        self.__overlay.hide()
            
    def _process_thumbnail(self, data):
        """
        New thumbnail has arrived from the data manager
        """
        # broadcast to all activity widgets
        for widget in self._activity_stream_data_widgets.values():
            widget.apply_thumbnail(data)

    def _process_new_note(self, activity_id, note_id):
        """
        A new note has arrived from the data manager
        """
        if activity_id in self._activity_stream_data_widgets:
            widget = self._activity_stream_data_widgets[activity_id]
            (reply_users, attachment_requests) = self._populate_note_widget(widget, activity_id, note_id)
            
            # request thumbs
            for attachment_req in attachment_requests:
                self._data_manager.request_attachment_thumbnail(attachment_req["activity_id"], 
                                                                attachment_req["attachment_group_id"], 
                                                                attachment_req["attachment_data"])
            
            for reply_user in reply_users:
                self._data_manager.request_user_thumbnail(reply_user["type"], 
                                                          reply_user["id"], 
                                                          reply_user["image"])
            self.note_arrived.emit(note_id)

        else:
            self.note_arrived.emit(note_id)

    def _on_entity_created(self, entity):
        """
        Callback when an entity is created by an underlying widget.

        :param entity:  The Shotgun entity that was created.
        """
        if entity["type"] == "Note":

            try:
                from sgtk.util.metrics import EventMetric

                fields = []  # reserved for future use
                annotations = {}  # reserved for future use

                properties = {
                    "Source": "Activity Stream",
                    "Linked Entity Type": entity.get("type", "Unknown"),
                    "Field Used": fields,
                    "Annotations": annotations
                }

                EventMetric.log(
                    EventMetric.GROUP_MEDIA,
                    "Created Note",
                    properties=properties,
                    bundle=self._bundle
                )
            except:
                # ignore all errors. ex: using a core that doesn't support metrics
                pass

            if self.notes_are_selectable:
                self._select_on_arrival = entity

        self.entity_created.emit(entity)
            
    def _on_reply_clicked(self, note_id):
        """
        Callback when someone clicks reply on a given note

        :param note_id: The id of the Shotgun Note entity being replied to.
        """
        self.reply_dialog.note_id = note_id

        # Position the reply modal dialog above the activity stream scroll area.
        pos = self.mapToGlobal(self.ui.activity_stream_scroll_area.pos())
        x_pos = pos.x() + (self.ui.activity_stream_scroll_area.width() / 2) - (self.reply_dialog.width() / 2) - 10         
        y_pos = pos.y() + (self.ui.activity_stream_scroll_area.height() / 2) - (self.reply_dialog.height() / 2) - 20
        self.reply_dialog.move(x_pos, y_pos)
        
        # and pop it
        try:
            self.__small_overlay.show()
            if self.reply_dialog.exec_() == QtGui.QDialog.Accepted:
                self.load_data(self._sg_entity_dict)

                try:
                    from sgtk.util.metrics import EventMetric

                    properties = {
                        "Source": "Activity Stream",
                    }

                    EventMetric.log(
                        EventMetric.GROUP_MEDIA,
                        "Created Reply",
                        properties=properties,
                        bundle=self._bundle
                    )
                except:
                    # ignore all errors. ex: using a core that doesn't support metrics
                    pass

        finally:
            self.__small_overlay.hide()

    def _load_shotgun_activity_stream(self):
        """
        Called when someone clicks 'show activity stream in shotgun'
        """
        url = "%s/detail/%s/%s" % (self._bundle.sgtk.shotgun_url, self._entity_type, self._entity_id)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    ############################################################################
    # events

    def mousePressEvent(self, event):
        """
        Overrides the default event handler in Qt.
        """
        if not self.notes_are_selectable:
            return

        # If they clicked on a note, select it. Any notes that were not
        # clicked on will be deselected.
        position = event.globalPos()

        for widget in self._activity_stream_data_widgets.values():
            if isinstance(widget, NoteWidget):
                selected = widget.underMouse()
                if selected != widget.selected:
                    widget.set_selected(selected)
                    self._note_selected_changed(selected, widget.note_id)


