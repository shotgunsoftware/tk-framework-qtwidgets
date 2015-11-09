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
from sgtk.platform.qt import QtCore, QtGui

class SmallOverlayWidget(QtGui.QWidget):
    """
    Simple overlay widget that darkens the background
    and prints a simple text.
    """
    MODE_OFF = 0
    MODE_ON = 1
    
    def __init__(self, parent):
        """
        Constructor
        """
        QtGui.QWidget.__init__(self, parent)
        
        self._bundle = sgtk.platform.current_bundle()
        
        # hook up a listener to the parent window so we 
        # can resize the overlay at the same time as the parent window
        # is being resized.
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)
        
        # make it transparent
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        
        # turn off the widget
        self.setVisible(False)
        self._mode = self.MODE_OFF
        
    ############################################################################################
    # public interface
    
    def show(self):
        """
        Turn on spinning
        """
        self.setVisible(True)
        self._mode = self.MODE_ON

    def hide(self):
        """
        Hide the overlay.
        """
        self._mode = self.MODE_OFF
        self.setVisible(False)
        
    ############################################################################################
    # internal methods
 
    def _on_parent_resized(self):
        """
        Special slot hooked up to the event filter.
        When associated widget is resized this slot is being called.
        """
        # resize overlay
        self.resize(self.parentWidget().size())
     
    def paintEvent(self, event):
        """
        Render the UI.
        """
        if self._mode == self.MODE_OFF:
            return
        
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            # set up semi transparent backdrop
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            overlay_color = QtGui.QColor(30, 30, 30, 160)
            painter.setBrush( QtGui.QBrush(overlay_color))
            painter.setPen(QtGui.QPen(overlay_color))
            painter.drawRect(0, 0, painter.device().width(), painter.device().height())            
        finally:
            painter.end()
        
class ResizeEventFilter(QtCore.QObject):
    """
    Event filter which emits a resized signal whenever
    the monitored widget resizes. This is so that the overlay wrapper
    class can be informed whenever the Widget gets a resize event.
    """
    resized = QtCore.Signal()

    def eventFilter(self,  obj,  event):
        # peek at the message
        if event.type() == QtCore.QEvent.Resize:
            # re-broadcast any resize events
            self.resized.emit()
        # pass it on!
        return False
