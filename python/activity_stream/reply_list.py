# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
from sgtk.platform.qt import QtCore, QtGui

from .dialog_reply import ReplyDialog

from .ui.reply_list_widget import Ui_ReplyListWidget

from .label_widgets import ClickableLabel
 
from .data_manager import ActivityStreamDataHandler
from .widget_attachment_group import AttachmentGroupWidget
from .widget_reply import ReplyWidget
from .overlaywidget import SmallOverlayWidget

utils = sgtk.platform.import_framework("tk-framework-shotgunutils", "utils")
 
class ReplyListWidget(QtGui.QWidget):
    """
    QT Widget that displays a note conversation, 
    including attachments and the ability to reply.

    This will first render the body of the note, including the attachments,
    and then subsequent replies. This widget uses the same
    widgets, data backend and visual components as the 
    activity stream.
    
    :signal entity_requested(str, int): Fires when someone clicks an entity inside
            the activity stream. The returned parameters are entity type and entity id.
    """
    
    # when someone clicks a link or similar
    entity_requested = QtCore.Signal(str, int)
    
    def __init__(self, parent):
        """
        :param parent: QT parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        """

        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyListWidget() 
        self.ui.setupUi(self)
        
        self._note_id = None
        self._sg_entity_dict = None
        self._task_manager = None
        self._general_widgets = []
        self._reply_widgets = []
        self._attachment_group_widgets = {}
        
        self._bundle = sgtk.platform.current_bundle()
        
        # apply styling
        self._load_stylesheet()
        
        # small overlay
        self.__small_overlay = SmallOverlayWidget(self)
        
        # create a data manager to handle backend
        self._data_manager = ActivityStreamDataHandler(self)
        
        self._data_manager.thumbnail_arrived.connect(self._process_thumbnail)
        self._data_manager.note_arrived.connect(self._process_note)
        
        
    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.
        
        :param task_manager: Background task manager to use
        :type task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager` 
        """
        self._data_manager.set_bg_task_manager(task_manager)
        self._task_manager = task_manager
        
    def destroy(self):
        """
        Should be called before the widget is closed
        """
        self._data_manager.destroy()
        self._task_manager = None
                    
    ##########################################################################################
    # public interface
        
    def load_data(self, sg_entity_dict):
        """
        Load replies for a given entity.
        
        :param sg_entity_dict: Shotgun link dictionary with keys type and id.
        """
        self._bundle.log_debug("Loading replies for %s" % sg_entity_dict)
        
        if sg_entity_dict["type"] != "Note":
            self._bundle.log_error("Can only show replies for Notes.")
            return

        # first ask the data manager to load up cached 
        # information about our note 
        self._sg_entity_dict = sg_entity_dict
        note_id = self._sg_entity_dict["id"]
        self._data_manager.load_note_data(note_id)

        # now attempt to render the note based on cached data
        self._process_note(activity_id=None, note_id=note_id)
        
        # and read in any updates in the background
        self._data_manager.rescan()


    ##########################################################################################
    # internal methods

    def _process_note(self, activity_id, note_id):
        """
        Callback that gets executed when note data arrives from
        the data manager.
        
        :param activiy_id: Activity stream id that this note is 
                           associated with. Note that in this case,
                           when we have requested a note outside
                           the context of the activity stream, this
                           value is undefined.
        :param note_id: Note id for the note for which data is available
                        in the data manager.
        """
        
        self._bundle.log_debug("Retrieved new data notification for "
                            "activity id %s, note id %s" % (activity_id, note_id))
        
        # set note content            
        note_thread_data = self._data_manager.get_note(note_id)
        
        if note_thread_data:            
            self._build_replies(note_thread_data)

    def _build_replies(self, note_thread_data):

        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes
        self.setVisible(False)
        
        try:
            
            ###############################################################
            # Phase 1 - render the UI.
            
            self._clear()
    
            note_id = self._sg_entity_dict["id"]            
            attachment_requests = []
            
            # first display the content of the note
            note_data = note_thread_data[0]
            
            note_content = note_data.get("content") or \
                           "This note does not have any content associated." 
            
            content_widget = QtGui.QLabel(self)
            content_widget.setWordWrap(True)
            content_widget.setText(note_content)
            content_widget.setObjectName("note_content_label")
            self.ui.reply_layout.addWidget(content_widget)
            self._general_widgets.append(content_widget)
            
            # we have cached note data
            replies_and_attachments = note_thread_data[1:] 
                        
            # now add replies
            self._add_replies_and_attachments(replies_and_attachments)
            
            # add a reply button and connect it
            reply_button = self._add_reply_button()
            reply_button.clicked.connect(lambda : self._on_reply_clicked(note_id))
    
            # add a proxy widget that should expand to fill all white
            # space available
            expanding_widget = QtGui.QLabel(self)
            self.ui.reply_layout.addWidget(expanding_widget)
            self.ui.reply_layout.setStretchFactor(expanding_widget, 1)
            self._general_widgets.append(expanding_widget)
    
            ###############################################################
            # Phase 2 - request additional data.
            # note that we don't interleave these requests with building
            # the ui - this is to minimise the risk of GIL signal issues
    
            # get all attachment data
            # can request thumbnails post UI build
            for attachment_group_id in self._attachment_group_widgets.keys():
                agw = self._attachment_group_widgets[attachment_group_id]
                for attachment_data in agw.get_data():                        
                    ag_request = {"attachment_group_id": attachment_group_id, 
                                  "attachment_data": attachment_data}
                    attachment_requests.append(ag_request)
    
            self._bundle.log_debug("Request thumbnails...")
            
            for attachment_req in attachment_requests:
                self._data_manager.request_attachment_thumbnail(-1, 
                                                                attachment_req["attachment_group_id"], 
                                                                attachment_req["attachment_data"])
            
            # now go through the shotgun data
            # for each reply, request a thumbnail.
            requested_items = []
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
                    reply_author = item["user"]
                    
                    uniqueness_key = (reply_author["type"], reply_author["id"])
                    if uniqueness_key not in requested_items:
                        # this thumbnail has not been requested yet    
                        if reply_author.get("image"):
                            # there is a thumbnail for this user!
                            requested_items.append(uniqueness_key)
                            self._data_manager.request_user_thumbnail(reply_author["type"], 
                                                                      reply_author["id"],
                                                                      reply_author["image"])
            
        finally:
            # make the window visible again and trigger a redraw
            self.setVisible(True)
            
        self._bundle.log_debug("...done")

        
    def _clear(self):
        """
        Clear the widget. This will remove all items from the UI
        """
        self._bundle.log_debug("Clearing UI...")
        
        for x in self._general_widgets + self._reply_widgets + self._attachment_group_widgets.values():
            # remove widget from layout:
            self.ui.reply_layout.removeWidget(x)
            # set it's parent to None so that it is removed from the widget hierarchy
            x.setParent(None)
            utils.safe_delete_later(x)
    
        self._general_widgets = []
        self._reply_widgets = []
        self._attachment_group_widgets = {}    
        
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
            
    def _add_reply_button(self):
        """
        Add a reply button to the stream of widgets
        """
        reply_button = ClickableLabel(self)
        reply_button.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        reply_button.setText("Reply to this Note")
        reply_button.setObjectName("reply_button")
        self.ui.reply_layout.addWidget(reply_button)
        self._general_widgets.append(reply_button)
        return reply_button

    def _add_attachment_group(self, attachments, after_note):
        """
        Add an attachments group to the stream of widgets
        """
        
        curr_attachment_group_widget_id = len(self._attachment_group_widgets)
        attachment_group = AttachmentGroupWidget(self, attachments)        
        
        # show an 'ATTACHMENTS' header
        attachment_group.show_attachments_label(True)        
        
        
        offset = attachment_group.OFFSET_NONE if after_note else attachment_group.OFFSET_LARGE_THUMB        
        attachment_group.adjust_left_offset(offset)
        
        self.ui.reply_layout.addWidget(attachment_group)
        
        # add it to our mapping dict and increment the counter
        self._attachment_group_widgets[curr_attachment_group_widget_id] = attachment_group
        
    def _add_replies_and_attachments(self, replies_and_attachments):
        """
        Add replies and attachment widgets to the stream of widgets
        
        :param replies_and_attachments: List of Shotgun data dictionary.
               These are eithere reply entities or attachment entities.
        """
        
        current_attachments = []
        attachment_is_directly_after_note = True
        
        for item in replies_and_attachments:

            if item["type"] == "Reply":
                
                # first, wrap up attachments
                if len(current_attachments) > 0:                    
                    self._add_attachment_group(current_attachments, attachment_is_directly_after_note)
                    current_attachments = []
                                                
                w = ReplyWidget(self)
                w.adjust_thumb_style(w.LARGE_USER_THUMB)
                self.ui.reply_layout.addWidget(w)
                w.set_info(item)
                self._reply_widgets.append(w)
                # ensure navigation requests from replies bubble up
                w.entity_requested.connect(self.entity_requested.emit)
                # next bunch of attachments will be after a reply
                # rather than directly under the note
                # (this affects the visual style)
                attachment_is_directly_after_note = False
                
            if item["type"] == "Attachment" and item["this_file"]["link_type"] == "upload":
                current_attachments.append(item)
        
        # see if there are still open attachments
        if len(current_attachments) > 0:
            self._add_attachment_group(current_attachments, attachment_is_directly_after_note)
            current_attachments = []            

    def _process_thumbnail(self, data):
        """
        Callback that gets called when a new thumbnail is available.
        Populate the UI with the given thumbnail
        
        :param data: dictionary with keys:
                     - thumbnail_type: thumbnail enum constant:
                            ActivityStreamDataHandler.THUMBNAIL_CREATED_BY
                            ActivityStreamDataHandler.THUMBNAIL_ENTITY
                            ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT
                     - activity_id: Activity stream id that this update relates
                       to. Note requests (which don't have an associated 
                       id, will use -1 to indicate this). 
                     
        
        QImage with thumbnail data
        :param thumbnail_type: thumbnail enum constant:
        """        
        thumbnail_type = data["thumbnail_type"]
        activity_id = data["activity_id"]
        image = data["image"]
        
        if thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT and activity_id == -1:
            group_id = data["attachment_group_id"]
            attachment_group = self._attachment_group_widgets[group_id]
            attachment_group.apply_thumbnail(data)

        elif thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_USER:
            # a thumbnail for a user possibly for one of our replies
            for reply_widget in self._reply_widgets:
                if reply_widget.thumbnail_populated:
                    # already set
                    continue
                if data["entity"] == reply_widget.created_by:
                    reply_widget.set_thumbnail(image)

    def _on_reply_clicked(self, note_id):
        """
        Callback when someone clicks reply to note
        
        :param note_id: Note id to reply to
        """
        
        # TODO - refactor to avoid having this code in two places
        
        # create reply dialog window
        reply_dialog = ReplyDialog(self, self._task_manager, note_id)
        
        # position the reply modal dialog above the activity stream scroll area
        pos = self.mapToGlobal(self.ui.reply_scroll_area.pos())
        x_pos = pos.x() + (self.ui.reply_scroll_area.width() / 2) - (reply_dialog.width() / 2) - 10         
        y_pos = pos.y() + (self.ui.reply_scroll_area.height() / 2) - (reply_dialog.height() / 2) - 20
        reply_dialog.move(x_pos, y_pos)
        
        # show the dialog, and while it's showing,
        # enable a transparent overlay on top of the existing replies
        # in order to make the reply window stand out.
        try:
            self.__small_overlay.show()
            if reply_dialog.exec_() == QtGui.QDialog.Accepted:
                self._data_manager.rescan()
                try:
                    from sgtk.util.metrics import EventMetric

                    properties = {
                        "Source": "Reply List",
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
        
        
