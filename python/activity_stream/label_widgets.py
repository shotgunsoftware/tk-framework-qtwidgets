# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.
"""
A collection of various subclassed QLabels used by the activity stream UI
"""
from sgtk.platform.qt import QtCore, QtGui
from . import utils
import sgtk

class ClickableLabel(QtGui.QLabel):
    """
    A label which can be clicked
    """
    clicked = QtCore.Signal()
    
    def __init__(self, parent):
        """
        Constructor

        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        QtGui.QLabel.__init__(self, parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        QtGui.QLabel.mousePressEvent(self, event)        
        self.clicked.emit()
    
    
class LargeAttachmentThumbnail(ClickableLabel):
    """
    A large, clickable attachment thumbnail
    """
    
    def __init__(self, data, parent):
        """
        Constructor
        
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        ClickableLabel.__init__(self, parent)
        self._bundle = sgtk.platform.current_bundle()
        
        # store shotgun data
        self._data = data
        
        if self._data["image"]:
            # a thumbnail exists for this attachment
            # set it up as a std event stream 254x144 chunk        
            self.setToolTip("Click to see full attachment.<br>"
                "File Name: %s" % self._data["this_file"]["name"])
            self.setMinimumSize(QtCore.QSize(256, 144))
            self.setMaximumSize(QtCore.QSize(256, 144))
            self.setText("")
            self.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/rect_256x144.png"))
        
        else:
            # no thumbnail for this guy
            self.setToolTip("Click to see full attachment.")
            self.setText(self._data["this_file"]["name"])
            self.setStyleSheet("""QLabel { 
                border-radius: 2px; 
                border: 1px solid rgba(200, 200, 200, 40%); 
                padding: 8px; 
                }""")
        
        
    def set_thumbnail(self, image):
        """
        Specify associated thumbnail
        
        :param image: Thumbnail
        :type image: :class:`PySide.QtGui.QPixmap`
        """
        thumb = utils.create_rectangular_256x144_thumbnail(image)
        self.setPixmap(thumb)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        ClickableLabel.mousePressEvent(self, event)        

        # {'attachment_links': [{'id': 6105,
        #                        'name': "Manne's Note on bunny_010_0050 - asdasdasdasd",
        #                        'type': 'Note'}],
        #  'created_at': 1438774776.0,
        #  'created_by': {'id': 38, 'name': 'Manne Ohrstrom', 'type': 'HumanUser'},
        #  'id': 266,
        #  'image': None,
        #  'this_file': {'content_type': 'application/pdf',
        #                'id': 266,
        #                'link_type': 'upload',
        #                'name': 'SustraMM_Costs_and_benefits_of_cycling.pdf',
        #                'type': 'Attachment',
        #                'url': 'https://manne-dev-1.shotgunstudio.com/file_serve/attachment/266'},
        #  'type': 'Attachment'}
        
        
        # {'attachment_links': [{'id': 6105,
        #                        'name': "Manne's Note on bunny_010_0050 - asdasdasdasd",
        #                        'type': 'Note'}],
        #  'created_at': 1438774085.0,
        #  'created_by': {'id': 38, 'name': 'Manne Ohrstrom', 'type': 'HumanUser'},
        #  'id': 265,
        #  'image': 'https://sg-media-usor-01.s3.amazonaws.com/...',
        #  'this_file': {'content_type': 'image/png',
        #                'id': 265,
        #                'link_type': 'upload',
        #                'name': 'screencapture_o9Pgb9.png',
        #                'type': 'Attachment',
        #                'url': 'https://sg-media-usor-01.s3.amazonaws.com/...'},
        #  'type': 'Attachment'}

        # the url to serve up attachments is on the form
        # https://manne-dev-1.shotgunstudio.com/file_serve/attachment/259/screencapture_3bVvcA.png
        
        file_name = self._data["this_file"]["name"]
        url = "%s/file_serve/attachment/%s/%s" % (self._bundle.sgtk.shotgun_url, self._data["id"], file_name)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        
        
class SmallAttachmentThumbnail(ClickableLabel):
    """
    A small, clickable attachment thumbnail
    """    
    def __init__(self, data, parent):
        """
        Constructor
        
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        ClickableLabel.__init__(self, parent)
        
        self.setMinimumSize(QtCore.QSize(48, 48))
        self.setMaximumSize(QtCore.QSize(48, 48))
        self.setScaledContents(True)
        self.setText("")
        self.setToolTip("Click to show a larger thumbnail.")
        self.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/attachment_icon_192px.png"))
        self._data = data
        
    def set_thumbnail(self, image):
        """
        Specify associated thumbnail
        
        :param image: Thumbnail
        :type image: :class:`PySide.QtGui.QPixmap`
        """        
        thumb = utils.create_square_48_thumbnail(image)
        self.setPixmap(thumb)




class UserThumbnail(ClickableLabel):
    """
    Subclassed QLabel to represent a shotgun user.
    """
    
    # signal that fires on click
    entity_requested = QtCore.Signal(str, int)
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        ClickableLabel.__init__(self, parent)
        # make this user clickable
        self._sg_data = None
            
    def set_shotgun_data(self, sg_data):
        """
        Set the shotgun data associated with this user
        
        :param sg_data: Shotgun user data
        """
        self._sg_data = sg_data
        user_name = sg_data.get("name") or "Unknown User"
        self.setToolTip(user_name)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        ClickableLabel.mousePressEvent(self, event)
        
        if self._sg_data:
            self.entity_requested.emit(self._sg_data["type"], self._sg_data["id"])
        
