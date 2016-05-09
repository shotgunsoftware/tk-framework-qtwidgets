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

class ShotgunPlaybackLabel(QtGui.QLabel):
    """
    Subclassed ``QLabel`` that displays a playback icon
    centered above its content.  
    
    While it is technically possible to use
    this label with text based content, we strongly recommend
    using it with a pixmap. Typically this is a Shotgun thumbnail.    
    
    By populating an instance with shotgun version data
    via the :meth:`set_shotgun_data()` method, the label
    will look at the data and determine whether a playback 
    icon should be displayed or not. In the case an icon is
    displayed, a playback_clicked signal may be emitted. 
    
    :signal playback_clicked(dict): The playback icon was clicked. 
        This signal passes the shotgun version data specified in
        via the :meth:`set_shotgun_data()` method back
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
        self._play_icon = QtGui.QPixmap(":/tk_framework_qtwidgets.version_label/play_icon.png")
        self._play_icon_inactive = QtGui.QPixmap(":/tk_framework_qtwidgets.version_label/play_icon_inactive.png")
        self._sg_data = None
        self._hover = False
        self._playable = False
        self._interactive = True

    def set_shotgun_data(self, sg_data):
        """
        Sets shotgun data associated with this label.
        This data will be used to drive the logic which is
        used to determine if the label should exhibit the playback icon or not.
        
        If you for example are passing a Shotgun data dictionary reprensenting
        a version, make sure to include the various quicktime and frame fields.
        
        :param sg_data: Shotgun data dictionary
        """
        self._sg_data = sg_data
        
        # based on the data, figure out if the icon should be active or not
        self._playable = False
        
        if sg_data and sg_data.get("type") == "Version":
            # versions are supported
            if sg_data.get("sg_uploaded_movie"):
                self._playable = True
        
        if self.playable and self.interactive:
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.unsetCursor() 
        
    @property    
    def playable(self):
        """
        Returns True if the label is playable given its current Shotgun data.
        """
        return self._playable

    def _get_interactive(self):
        """
        Whether a playable label is interactive. If it is not, then the play
        icon will not be overlayed on the thumbnail image, and the playback
        signal will not be emitted on click event.
        """
        return self._interactive

    def _set_interactive(self, state):
        self._interactive = bool(state)

        if self.playable and self._interactive:
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.unsetCursor() 

    interactive = QtCore.Property(
        bool,
        _get_interactive,
        _set_interactive,
    )
    
    def enterEvent(self, event):
        """
        Fires when the mouse enters the widget space
        """
        QtGui.QLabel.enterEvent(self, event)
        if self.playable and self.interactive:
            self._hover = True
            self.repaint()
        
    def leaveEvent(self, event):
        """
        Fires when the mouse leaves the widget space
        """
        QtGui.QLabel.leaveEvent(self, event)
        if self.playable and self.interactive:
            self._hover = False
            self.repaint()

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed
        """
        QtGui.QLabel.mousePressEvent(self, event)
        if self.playable and self._hover and self.interactive:
            self.playback_clicked.emit(self._sg_data)
        
    def paintEvent(self, event):
        """
        Render the UI.
        """
        # first render the label
        QtGui.QLabel.paintEvent(self, event)
        
        if self.playable and self.interactive:
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
 
