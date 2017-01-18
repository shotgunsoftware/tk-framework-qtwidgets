# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui

import sgtk

from .widget_activity_stream_base import ActivityStreamBaseWidget
from .ui.note_widget import Ui_NoteWidget

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from .widget_reply import ReplyWidget

from .label_widgets import ClickableLabel

from .widget_attachment_group import AttachmentGroupWidget
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")

from .data_manager import ActivityStreamDataHandler
from . import utils

class NoteWidget(ActivityStreamBaseWidget):
    """
    Widget that represents a Note. This widget in turn contains
    replies and attachments.

    :signal selection_changed(bool, int): Fires when the selection state of the widget
        changes. The first argument provided is a boolean based on whether the widget
        was selected or deselected, and the second is the Note entity ID associated
        with the widget.
    """

    # Whether this was a selection or a deselection, followed by the
    # Note entity ID associated with this widget.
    selection_changed = QtCore.Signal(bool, int)
    
    def __init__(self, note_id, parent):
        """
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`        
        """
        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteWidget() 
        self.ui.setupUi(self)
        
        self._note_id = note_id
        self._general_widgets = []
        self._reply_widgets = []
        self._attachment_group_widgets = {}
        self._selected = False
        self._attachments = []
        self._show_note_links = True
        self._attachments_filter = None

        # We set a transparent border initially, because we don't want to
        # see the widget "jump" in its size/placement when it is selected
        # and the colored border appears.
        self.setStyleSheet("#frame { border: 1px solid rgba(255,255,255, 20%) }")
        self.set_selected(False)

        # make sure clicks propagate upwards in the hierarchy
        self.ui.content.linkActivated.connect(self._entity_request_from_url)
        self.ui.header_left.linkActivated.connect(self._entity_request_from_url)    
        self.ui.user_thumb.entity_requested.connect(
            lambda entity_type, entity_id: self.entity_requested.emit(
                entity_type,
                entity_id
            )
        )

    ##############################################################################
    # properties

    @property
    def attachments(self):
        """
        Returns a list of attachment entities as returned from the
        Shotgun Python API.

        Example:
        [
            {'attachment_links': [{'id': 6043,
                                   'name': "Jeff's Note on Buck_rig_v01, Buck - Test!",
                                   'type': 'Note'}],
             'created_at': 1467064531.0,
             'created_by': {'id': 39, 'name': 'Jeff Beeland', 'type': 'HumanUser'},
             'id': 597,
             'image': 'https://abc.shotgunstudio.com/thumbnail/api_image/7207?AccessKeyId=123&Expires=123&Signature=123',
             'this_file': {'content_type': 'image/png',
                           'id': 597,
                           'link_type': 'upload',
                           'name': 'test.png',
                           'type': 'Attachment',
                           'url': 'https://abc.shotgunstudio.com/file_serve/attachment/597'},
             'type': 'Attachment'}
        ]
        """
        return self._attachments

    @property
    def note_id(self):
        """
        The Note entity id that this widget is representing.
        """
        return self._note_id

    @property
    def selected(self):
        """
        Whether the widget is currently considered to be selected.

        :returns:   bool
        """
        return self._selected

    @property
    def user_thumb(self):
        """
        The user thumbnail widget.
        """
        return self.ui.user_thumb

    def _get_show_note_links(self):
        """
        Whether the widget will contain a list of navigation links for
        the parent shot/version/task entities.
        """
        return self._show_note_links

    def _set_show_note_links(self, state):
        self._show_note_links = bool(state)

    show_note_links = property(_get_show_note_links, _set_show_note_links)

    def _get_attachments_filter(self):
        """
        If set to a compiled regular expression, attachment file names that match
        will be filtered OUT and NOT shown.
        """
        return self._attachments_filter

    def _set_attachments_filter(self, regex):
        self._attachments_filter = regex

    attachments_filter = property(_get_attachments_filter, _set_attachments_filter)

    ##############################################################################
    # public interface

    def set_user_thumb_cursor(self, cursor):
        """
        Sets the cursor displayed when hovering over the user
        thumbnail.

        :param cursor: The Qt cursor to set.
        """
        self.user_thumb.setCursor(cursor)

        for widget in self._reply_widgets:
            widget.set_user_thumb_cursor(cursor)
    
    def set_info(self, data):
        """
        Populate text fields for this widget
        
        :param data: data dictionary with activity stream info. 
        """        
        # call base class
        ActivityStreamBaseWidget.set_info(self, data)
        
        # most of the info will appear later, as part of the note
        # data being loaded, so add placeholder
        self.ui.content.setText("Hang on, loading note content...")
        
    def apply_thumbnail(self, data):
        """
        Populate the UI with the given thumbnail
        
        :param image: QImage with thumbnail data
        :param thumbnail_type: thumbnail enum constant:
            ActivityStreamDataHandler.THUMBNAIL_CREATED_BY
            ActivityStreamDataHandler.THUMBNAIL_ENTITY
            ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT
        """        
        thumbnail_type = data["thumbnail_type"]
        activity_id = data["activity_id"]
        image = data["image"]
        
        if thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_CREATED_BY and activity_id == self.activity_id:
            thumb = utils.create_round_thumbnail(image)          
            self.ui.user_thumb.setPixmap(thumb)
        
        elif thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT and activity_id == self.activity_id:
            group_id = data["attachment_group_id"]
            attachment_group = self.get_attachment_group_widget(group_id)
            attachment_group.apply_thumbnail(data)

        elif thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_USER:
            # a thumbnail for a user possibly for one of our replies
            for reply_widget in self._reply_widgets:
                if reply_widget.thumbnail_populated:
                    # already set
                    continue
                if data["entity"] == reply_widget.created_by:
                    reply_widget.set_thumbnail(image)


    def add_reply_button(self):
        reply_button = ClickableLabel(self)
        reply_button.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        reply_button.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Maximum,
                QtGui.QSizePolicy.Preferred,
            )
        )
        button_layout = QtGui.QHBoxLayout()
        self.ui.reply_layout.addLayout(button_layout)
        button_layout.addStretch(1)
        button_layout.addWidget(reply_button)
        reply_button.setText("Reply to this Note")
        reply_button.setObjectName("reply_button")
        self._general_widgets.extend([reply_button, button_layout])
        return reply_button

    def get_attachment_group_widget_ids(self):
        return self._attachment_group_widgets.keys()
    
    def get_attachment_group_widget(self, attachment_group_id):
        """
        Returns an attachment group widget given its id
        """
        return self._attachment_group_widgets[attachment_group_id]
    
    def add_replies(self, replies_and_attachments):
        """
        Add replies and attachment widgets
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
                w.set_user_thumb_cursor(self.user_thumb.cursor())

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
                self._attachments.append(item)

        # see if there are still open attachments
        if len(current_attachments) > 0:                    
            self._add_attachment_group(current_attachments, attachment_is_directly_after_note)
            current_attachments = []

    def set_selected(self, state):
        """
        Sets the selection state of the widget.

        :param state:   Whether the widget is to be selected or deselected.
        :type state:    bool
        """
        if bool(state) == self.selected:
            return

        self._selected = bool(state)

        if self.selected:
            color = self.palette().color(
                QtGui.QPalette.Normal,
                QtGui.QPalette.Highlight
            )
            self.setStyleSheet(
                "#frame { border: 1px solid rgb(%s,%s,%s) }" % (
                    color.red(),
                    color.green(),
                    color.blue()
                )
            )
        else:
            self.setStyleSheet("#frame { border: 1px solid rgba(255,255,255, 20%) }")

        self.selection_changed.emit(self.selected, self._note_id)
        
    def _add_attachment_group(self, attachments, after_note):
        """
        
        """
        curr_attachment_group_widget_id = len(self._attachment_group_widgets)
        attachment_group = AttachmentGroupWidget(
            parent=self,
            attachment_data=attachments,
            filter_regex=self.attachments_filter,
        )
        # don't show the ATTACHMENTS header in the activity stream
        attachment_group.show_attachments_label(False)        

        offset = attachment_group.OFFSET_NONE if after_note else attachment_group.OFFSET_SMALL_THUMB        
        attachment_group.adjust_left_offset(offset)
        
        self.ui.reply_layout.addWidget(attachment_group)
        
        # add it to our mapping dict and increment the counter
        self._attachment_group_widgets[curr_attachment_group_widget_id] = attachment_group
        
        
    def __generate_note_links_table(self, links):
        """
        Make a html table that contains links different items
        """
        # format note links
        html_chunks = []
        for link in links:
            entity_type_display_name = shotgun_globals.get_type_display_name(link["type"])
 
            chunk = """
                <tr><td bgcolor=#666666>
                    <a href='%s:%s' style='text-decoration: none; color: #dddddd'>%s %s</a>
                </td></tr>
                """ % (link["type"], link["id"], entity_type_display_name, link["name"])
            html_chunks.append(chunk)

        html = """
        <table cellpadding=5 cellspacing=2 >
        %s
        </table>
        """ % "\n".join(html_chunks)
        
        return html
        

    def set_note_info(self, data):
        """
        update with new note data
        """
        
        self._note_id = data["id"]
        
        # make the thumbnail clickable
        self.ui.user_thumb.set_shotgun_data(data["user"])
        
        # the top left part of the note is the name of the author
        entity_url = self._generate_entity_url(data["user"], 
                                               this_syntax=False,
                                               display_type=False)        
        self.ui.header_left.setText("%s" % entity_url)
        
        # top right is the date of the note (rather than 
        # date of activity)
        self._set_timestamp(data, self.ui.date)
        
        # Set the main note text. For this, and for the note links and
        # task keys below, we are treating it with kids gloves to make
        # sure that we don't end up raising a KeyError in a way that
        # makes it to the user. This is due to the possibility of having
        # a malformed Cut entity in Shotgun and SHOULD be handled at a
        # higher level than this widget, but we're still going to be
        # careful here, because we saw this bug crop up during Cut Support
        # QA.
        self.ui.content.setText(data.get("content", ""))

        # This allows selections from higher-level layouts to occur. If
        # we don't set this, the label accepts and blocks mouse click
        # events, which means if you expect to select the note widget
        # itself you can't click on the note contents.
        self.ui.content.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        
        # format note links
        if self.show_note_links:
            html_link_box_data = data.get("note_links", []) + data.get("tasks", [])
            links_html = self.__generate_note_links_table(html_link_box_data)
            self.ui.links.setText(links_html)
