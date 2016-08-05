# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import re

from sgtk.platform.qt import QtCore, QtGui
import sgtk

from .label_widgets import LargeAttachmentThumbnail, SmallAttachmentThumbnail
from .data_manager import ActivityStreamDataHandler

from .ui.attachment_group_widget import Ui_AttachmentGroupWidget

class AttachmentGroupWidget(QtGui.QWidget):
    """
    Widget that acts as a container for note attachments.
    This holds both a scaled down preview and a large size
    representation of a set of given attachments.
    """
    
    OFFSET_NONE, OFFSET_LARGE_THUMB, OFFSET_SMALL_THUMB = range(3)
    
    def __init__(self, parent, attachment_data, filter_regex=None):
        """
        Constructor
        
        :param parent: QT parent object
        :param dict attachment_data: The attachment data from Shotgun to represent.
        :param filter_regex: A compiled regular expression used to filter OUT matching
                             attachments based on file basename.
        :type filter_regex: SRE_Pattern (re.compile return type)
        """
        QtGui.QWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_AttachmentGroupWidget() 
        self.ui.setupUi(self)
        
        self._bundle = sgtk.platform.current_bundle()
        
        self._large_thumbnails = {}
        self._small_thumbnails = {}
        self._other_widgets = []
        self._filter_regex = filter_regex
        
        self._attachment_data = attachment_data
        
        self.ui.attachment_frame.setVisible(False)
        
        current_row = 0
        current_col = 0
        max_col = 0
        
        for data in self._attachment_data:
            
            if self._filter_regex:
                if re.match(self._filter_regex, str(data.get("this_file", dict()).get("name"))):
                    continue
            obj = SmallAttachmentThumbnail(data, self.ui.preview_frame)
            obj.clicked.connect(self._toggle_large_thumbnails)            
            self.ui.preview_layout.addWidget(obj, current_row, current_col)
            self._small_thumbnails[data["id"]] = obj
            
            
            if current_col > 4:
                current_col = 0
                current_row += 1
            else:
                current_col += 1
                
            # track the max column used so far
            max_col = max(current_col, max_col)
            
        
        # and have everything pushed to the left        
        self.ui.preview_layout.setColumnStretch(max_col+1, 1)
        
        # now populate the large thumbs - they reside in a hidden 
        # frame in the UI
        
        # first, add a button to allow for the collapse of the UI
        hide_preview_button = QtGui.QPushButton(self)
        hide_preview_button.setText("Click to hide preview")
        hide_preview_button.setObjectName("hide_preview_button")
        hide_preview_button.setCursor(QtCore.Qt.PointingHandCursor)
        hide_preview_button.setFocusPolicy(QtCore.Qt.NoFocus)
        hide_preview_button.clicked.connect(self._toggle_small_thumbnails)        
        self.ui.attachment_layout.addWidget(hide_preview_button)
        self._other_widgets.append(hide_preview_button)
        
        for data in self._attachment_data:
            if self._filter_regex:
                if re.match(self._filter_regex, str(data.get("this_file", dict()).get("name"))):
                    continue
            obj = LargeAttachmentThumbnail(data, self)
            self.ui.attachment_layout.addWidget(obj)
            self._large_thumbnails[data["id"]] = obj

    ##############################################################################
    # properties

    @property
    def filter_regex(self):
        """
        If set to a compiled regular expression, attachment file names that match
        will be filtered OUT and NOT shown.
        """
        return self._filter_regex


    ##############################################################################
    # methods
        
    def show_attachments_label(self, status):
        """
        Toggle whether the text ATTACHMENTS should be visible or not
        """
        self.ui.attachments_label.setVisible(status)
        
    def adjust_left_offset(self, offset):
        """
        Set left offset
        """
        if offset == self.OFFSET_NONE:
            self.ui.verticalLayout.setContentsMargins(0, 6, 0, 0)
        elif offset == self.OFFSET_LARGE_THUMB:
            self.ui.verticalLayout.setContentsMargins(60, 6, 0, 0)
        elif offset == self.OFFSET_SMALL_THUMB:
            self.ui.verticalLayout.setContentsMargins(36, 6, 0, 0)
        else:
            self._bundle.log_warning("Unknown offset for attachment group")
        
    def apply_thumbnail(self, data):
        """
        set thumbnail
        """
        if data["thumbnail_type"] != ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT:
            return

        attachment_id = data["entity"]["id"]
        if attachment_id in self._large_thumbnails:
            attachment_obj = self._large_thumbnails[attachment_id]
            attachment_obj.set_thumbnail(data["image"])
            
        if attachment_id in self._small_thumbnails:
            attachment_obj = self._small_thumbnails[attachment_id]
            attachment_obj.set_thumbnail(data["image"])

    def _toggle_large_thumbnails(self):
        
        self.ui.attachment_frame.setVisible(True)
        self.ui.preview_frame.setVisible(False)
        
    def _toggle_small_thumbnails(self):
        
        self.ui.attachment_frame.setVisible(False)
        self.ui.preview_frame.setVisible(True)

    def get_data(self):
        return self._attachment_data
            
        
