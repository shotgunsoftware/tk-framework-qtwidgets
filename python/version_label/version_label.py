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

from .ui import resources_rc

class VersionLabel(QtGui.QLabel):
    """
    Subclassed QLabel that displays a playback icon
    centered above the existing pixmap.
    
    By populating an instance with shotgun version data
    via the set_shotgun_data() method, the version label
    will look at the data and determine whether a playback 
    icon should be displayed or not. In the case an icon is
    displayed, a playback_clicked signal may be emitted. 
    
    This signal passes the same shotgun version data back
    to the caller.   
    """
    
    # signal fires when the play button was clicked
    playback_clicked = QtCore.Signal(dict)
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QLabel.__init__(self, parent)
        self._play_icon = QtGui.QPixmap(":/tk_multi_infopanel_version_label/play_icon.png")
        self._play_icon_inactive = QtGui.QPixmap(":/tk_multi_infopanel_version_label/play_icon_inactive.png")
        self._sg_data = None
        self._hover = False
        self._active = False

    def set_shotgun_data(self, sg_data):
        """
        Sets version data associated with this label
        """
        self._sg_data = sg_data
        
        # based on the data, figure out if the icon should be active or not
        self._active = False
        
        if sg_data and sg_data.get("type") == "Version":
            # versions are supported
            if sg_data.get("sg_uploaded_movie"):
                self._active = True
        
        if self._active:
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.unsetCursor() 
            
    def enterEvent(self, event):
        """
        Fires when the mouse enters the widget space
        """
        QtGui.QLabel.enterEvent(self, event)
        if self._active:
            self._hover = True
            self.repaint()
        
    def leaveEvent(self, event):
        """
        Fires when the mouse leaves the widget space
        """
        QtGui.QLabel.leaveEvent(self, event)
        if self._active:
            self._hover = False
            self.repaint()

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        QtGui.QLabel.mousePressEvent(self, event)
        if self._active and self._hover:
            self.playback_clicked.emit(self._sg_data)
        
    def paintEvent(self, event):
        """
        Render the UI.
        """
        # first render the label
        QtGui.QLabel.paintEvent(self, event)
        
        if self._active:
            # now render a pixmap on top
            painter = QtGui.QPainter()
            painter.begin(self)
            try:
                # set up semi transparent backdrop
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                
                # draw image
                painter.translate((painter.device().width() / 2) - (self._play_icon.width()/2), 
                                  (painter.device().height() / 2) - (self._play_icon.height()/2) )
                
                if self._hover:
                    painter.drawPixmap( QtCore.QPoint(0, 0), self._play_icon)
                else:
                    painter.drawPixmap( QtCore.QPoint(0, 0), self._play_icon_inactive)
                    
            finally:
                painter.end()
 
