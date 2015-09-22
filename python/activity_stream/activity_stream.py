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
 
overlay_module = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")

from .overlaywidget import SmallOverlayWidget
 
class ActivityStreamWidget(QtGui.QWidget):
    """
    Widget that displays the Shotgun activity stream for an entity.
    """
    
    # max number of items to show in the activity stream.
    MAX_STREAM_LENGTH = 20
    
    # when someone clicks a link or similar
    entity_requested = QtCore.Signal(str, int)
    playback_requested = QtCore.Signal(dict)    
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        self._app = sgtk.platform.current_bundle()
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ActivityStreamWidget() 
        self.ui.setupUi(self)
        
        # apply styling
        self._load_stylesheet()

        # keep an overlay for loading
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
        self.ui.note_widget.data_updated.connect(self._on_note_submitted)
        
        # keep handles to all widgets to be nice to the GC
        self._loading_widget = None
        self._other_widgets = []
        self._widgets = {}
                
        # state management
        self._data_retriever = None
        self._sg_entity_dict = None
        self._entity_type = None
        self._entity_id = None
        
    def set_data_retriever(self, data_retriever):
        """
        Set an async data retreiver object to use with this widget.
        """
        self._data_retriever = data_retriever
        self._data_manager.set_data_retriever(data_retriever)
        self.ui.note_widget.set_data_retriever(data_retriever)
        
    ############################################################################
    # public interface
        
    def load_data(self, sg_entity_dict):
        """
        Reset the state of the widget and then load up the data
        for the given entity.
        
        :param sg_entity_dict: Dictionary with keys type and id.
        """
        self._app.log_debug("Setting up activity stream for entity %s" % sg_entity_dict)
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
        if self._entity_type in ["ApiUser", "HumanUser", "ClientUser"]:
            self.ui.note_widget.setVisible(False)
        else:
            self.ui.note_widget.setVisible(True)

        # now load cached data for the given entity
        self._app.log_debug("Setting up db manager....")
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
        self._app.log_debug("Start building widgets based on cached data...")
        self.setVisible(False)
        try:

            # we are building the widgets bottom up.
            # first of all, insert a widget that will expand so that 
            # it consumes all unused space. This is to keep other
            # widgets from growing when there are only a few widgets
            # available in the scroll area.
            self._app.log_debug("Adding expanding base widget...")            
            
            expanding_widget = QtGui.QLabel(self)
            self.ui.activity_stream_layout.addWidget(expanding_widget)
            self.ui.activity_stream_layout.setStretchFactor(expanding_widget, 1)
            self._other_widgets.append(expanding_widget)

            sg_stream_button = QtGui.QPushButton(self)
            sg_stream_button.setText("Click here to see the Activity stream in Shotgun.")
            sg_stream_button.setObjectName("full_shotgun_stream_button")
            sg_stream_button.setCursor(QtCore.Qt.PointingHandCursor)
            sg_stream_button.setFocusPolicy(QtCore.Qt.NoFocus)
            sg_stream_button.clicked.connect(self._load_shotgun_activity_stream)
            
            self.ui.activity_stream_layout.addWidget(sg_stream_button)
            self._other_widgets.append(sg_stream_button)
    
            # ids are returned in async order. Now pop them onto the activity stream,
            # old items first order...
            self._app.log_debug("Adding activity widgets...")
            for activity_id in ids_to_process:
                w = self._create_activity_widget(activity_id)
                # note that not all activity data entries generate
                # a widget in our factory method.      
                if w:
                    # a widget was generated! Insert it into
                    # the widget layouts etc.
                    self._widgets[activity_id] = w
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
            # to put at the top of the list
            self._app.log_debug("Adding loading widget...")
            self._loading_widget = QtGui.QLabel(self)
            self._loading_widget.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
            self._loading_widget.setText("Loading data from Shotgun...") 
            self._loading_widget.setObjectName("loading_widget")
            self.ui.activity_stream_layout.addWidget(self._loading_widget)
        
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            self._app.log_debug("...UI building complete!")
                
        ###############################################################
        # Phase 2 - request additional data.
        # note that we don't interleave these requests with building
        # the ui - this is to minimise the risk of GIL signal issues
                
        # request thumbs
        self._app.log_debug("Request thumbnails...")
        for activity_id in ids_to_process:
            self._data_manager.request_activity_thumbnails(activity_id)
        
        for attachment_req in attachment_requests:
            self._data_manager.request_attachment_thumbnail(attachment_req["activity_id"], 
                                                            attachment_req["attachment_group_id"], 
                                                            attachment_req["attachment_data"])
        
        # now request thumbnails for all usesr who have replied, but 
        # only once per user
        reply_users_dup_check = []
        for reply_user in all_reply_users:
            
            unique_user = (reply_user["type"], reply_user["id"]) 
            
            if unique_user not in reply_users_dup_check: 
                reply_users_dup_check.append(unique_user)
                self._data_manager.request_user_thumbnail(reply_user["type"], 
                                                          reply_user["id"],
                                                          reply_user["image"])
        
        self._app.log_debug("...done")
        
        # and now request an update check
        self._app.log_debug("Ask db manager to ask shotgun for updates...")
        self._data_manager.rescan()
        self._app.log_debug("...done")
            
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
        self._app.log_debug("Clearing UI...")
        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes        
        self.setVisible(False)
        
        # scroll to top
        self.ui.activity_stream_scroll_area.verticalScrollBar().setValue(0)
        
        try:
            self._app.log_debug("Clear loading widget")
            self._clear_loading_widget()

            self._app.log_debug("Removing all widget items")
            for x in self._widgets.values():
                # remove widget from layout:
                self.ui.activity_stream_layout.removeWidget(x)
                # set it's parent to None so that it is removed from the widget hierarchy
                x.setParent(None)
                # mark it to be deleted when event processing returns to the main loop
                x.deleteLater()
        
            self._app.log_debug("Clearing python data structures")
            self._widgets = {}
    
            self._app.log_debug("Removing expanding widget")
            for w in self._other_widgets:
                self.ui.activity_stream_layout.removeWidget(w)
                w.setParent(None)
                w.deleteLater()
            self._other_widgets = []
        
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            
    def _clear_loading_widget(self):
        """
        Remove the loading widget from the widget list
        """
        if self._loading_widget:
            self._app.log_debug("Cleaning the loading widget")
            self.ui.activity_stream_layout.removeWidget(self._loading_widget)
            self._loading_widget.setParent(None)
            self._loading_widget.deleteLater()
            self._loading_widget = None
            self._app.log_debug("...done")
        
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
        returns None
        """
        data = self._data_manager.get_activity_data(activity_id)
        
        widget = None
        
        # factory logic
        if data["update_type"] == "create":
            
            if data["primary_entity"]["type"] in ["Version", "PublishedFile", "TankPublishedFile"]:
                # full on 'new item' widget with thumbnail, description etc.
                widget = NewItemWidget(self)
            
            elif data["primary_entity"]["type"] == "Note":
                # new note
                widget = NoteWidget(self)
                
            else:
                # minimalistic 'new' widget for all other cases
                widget = SimpleNewItemWidget(self)
                            
        elif data["update_type"] == "create_reply":
            widget = NoteWidget(self)
            
        elif data["update_type"] == "update":
            widget = ValueUpdateWidget(self)
            
        else:
            self._app.log_debug("Activity type not supported and will not be "
                                "rendered: %s" % data["update_type"])
        
        # initialize the widget
        if widget:
            widget.set_host_entity(self._entity_type, self._entity_id)
            widget.set_info(data)
            widget.entity_requested.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))
            widget.playback_requested.connect(lambda sg_data: self.playback_requested.emit(sg_data))
                    
        return widget
        
    def _process_new_data(self, activity_ids):
        """
        New activity items have arrived from from the data manager
        """
        self._app.log_debug("Process new data slot called "
                            "for %s activity events" % len(activity_ids))
                
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
            self._app.log_debug("Capping the %s new activity items down to "
                                "%s items" % (len(activity_ids), self.MAX_STREAM_LENGTH))
        
            # transform [10,11,12,13,14,15,16,17] -> [15,16,17]
            activity_ids = activity_ids[-self.MAX_STREAM_LENGTH:]
        
        for activity_id in activity_ids:
            self._app.log_debug("Creating new widget...")
            w = self._create_activity_widget(activity_id)
            if w:            
                self._widgets[activity_id] = w
                self._app.log_debug("Adding %s to layout" % w)
                self.ui.activity_stream_layout.addWidget(w)        
                # add special blue border to indicate that this is a new arrival
                w.setStyleSheet("QFrame#frame{ border: 1px solid rgba(48, 167, 227, 50%); }")
        
        # when everything is loaded in, load the thumbs
        self._app.log_debug("Requesting thumbnails")
        for activity_id in activity_ids:
            self._data_manager.request_activity_thumbnails(activity_id)
                
        self._app.log_debug("Process new data complete.")

        # turn off the overlay in case it is spinning
        # (which only happens on a full load)
        self.__overlay.hide()
            
    def _process_thumbnail(self, data):
        """
        New thumbnail has arrived from the data manager
        """
        # broadcast to all activity widgets
        for widget in self._widgets.values():
            widget.set_thumbnail(data)

    def _process_new_note(self, activity_id, note_id):
        """
        A new note has arrived from the data manager
        """
        if activity_id in self._widgets:
            widget = self._widgets[activity_id]
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
            
    def _on_reply_clicked(self, note_id):
        """
        Callback when someone clicks reply on a given note
        """
        reply_dialog = ReplyDialog(self, self._data_retriever, note_id)
        
        #position the reply modal dialog above the activity stream scroll area
        pos = self.mapToGlobal(self.ui.activity_stream_scroll_area.pos())
        x_pos = pos.x() + (self.ui.activity_stream_scroll_area.width() / 2) - (reply_dialog.width() / 2) - 10         
        y_pos = pos.y() + (self.ui.activity_stream_scroll_area.height() / 2) - (reply_dialog.height() / 2) - 20
        reply_dialog.move(x_pos, y_pos)
        
        # and pop it
        
        try:
            self.__small_overlay.show()
            if reply_dialog.exec_() == QtGui.QDialog.Accepted:
                self.load_data(self._sg_entity_dict)
        finally:
            self.__small_overlay.hide()
        
    def _on_note_submitted(self):
        """
        called when a note has finished submitting
        """
        # kick the data manager to rescan for changes
        self._data_manager.rescan()

    def _load_shotgun_activity_stream(self):
        """
        Called when someone clicks 'show activity stream in shotgun'
        """
        url = "%s/detail/%s/%s" % (self._app.sgtk.shotgun_url, self._entity_type, self._entity_id)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

