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

from .widget_activity_stream_base import ActivityStreamBaseWidget
from .ui.reply_widget import Ui_ReplyWidget

from . import utils

class ReplyWidget(ActivityStreamBaseWidget):
    """
    Widget that shows a reply to a note.
    """
    
    (LARGE_USER_THUMB, SMALL_USER_THUMB) = range(2)
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyWidget() 
        self.ui.setupUi(self)
        
        self._data = None
        self._thumbnail_populated = False
        self._thumbnail_url = None
        
        # make sure clicks propagate upwards in the hierarchy
        self.ui.reply.linkActivated.connect(self._entity_request_from_url)
        self.ui.header_left.linkActivated.connect(self._entity_request_from_url)    
        
        self.ui.user_thumb.entity_requested.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))

    ##############################################################################
    # properties

    @property
    def user_thumb(self):
        """
        The user thumbnail widget.
        """
        return self.ui.user_thumb

    ##############################################################################
    # public interface

    def adjust_thumb_style(self, style):
        
        if style == self.LARGE_USER_THUMB:
            self.ui.user_thumb.setMinimumSize(QtCore.QSize(50, 50))
            self.ui.user_thumb.setMaximumSize(QtCore.QSize(50, 50))
        elif style == self.SMALL_USER_THUMB:
            self.ui.user_thumb.setMinimumSize(QtCore.QSize(30, 30))
            self.ui.user_thumb.setMaximumSize(QtCore.QSize(30, 30))
        else:
            self._bundle.log_warning("Unknown thumb style for reply")

    def set_user_thumb_cursor(self, cursor):
        """
        Sets the cursor displayed when hovering over the user
        thumbnail.

        :param cursor: The Qt cursor to set.
        """
        self.user_thumb.setCursor(cursor)

    @property
    def note_widget(self):
        """
        Returns the NoteInputWidget wrapped by the ReplyDialog.
        """
        return self.ui.note_widget
        
    @property
    def thumbnail_url(self):
        return self._thumbnail_url

    @property
    def thumbnail_populated(self):
        return self._thumbnail_populated
    
    @property
    def created_by(self):
        """
        Return the creator of this note, as a type/id dict
        """
        return {"type": self._data["user"]["type"], "id": self._data["user"]["id"] } 

    def set_info(self, data):
        """
        Populate text fields for this widget
        
        :param data: data dictionary with activity stream info. 
        """        
        # call base class
        #ActivityStreamBaseWidget.set_info(self, data)
        
        self._data = data
        
        self.ui.user_thumb.set_shotgun_data(data["user"])
        
        self._thumbnail_url = data["user"].get("image")
        
        entity_url = self._generate_entity_url(data["user"], 
                                               this_syntax=False,
                                               display_type=False)
        
        # set standard date field
        self._set_timestamp(data, self.ui.date)
        
        self.ui.header_left.setText("%s" % entity_url)
        
        self.ui.reply.setText(data["content"])
        

    def set_thumbnail(self, image):
        """
        Populate the UI with the given thumbnail        
        """
        self._thumbnail_populated = True
        thumb = utils.create_round_thumbnail(image)          
        self.ui.user_thumb.setPixmap(thumb)

