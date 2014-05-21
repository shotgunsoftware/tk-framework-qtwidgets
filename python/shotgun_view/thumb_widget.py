# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import tank

from tank.platform.qt import QtCore, QtGui
from .ui.thumb_widget import Ui_ThumbWidget

class ThumbWidget(QtGui.QWidget):
    """
    Thumbnail style widget which contains an image and some 
    text underneath. The widget scales gracefully.
    
    This class is typically used in conjunction with a QT View and the 
    ShotgunDelegate class.     
    """
    
    def __init__(self, parent):
        """
        Constructor
        """
        QtGui.QWidget.__init__(self, parent)

        # make sure this widget isn't shown
        self.setVisible(False)
        
        # set up the UI
        self.ui = Ui_ThumbWidget() 
        self.ui.setupUi(self)
        
        # set up an event filter to ensure that the thumbnails
        # are scaled in a square fashion.
        filter = ResizeEventFilter(self.ui.thumbnail)
        filter.resized.connect(self.__on_thumb_resized)
        self.ui.thumbnail.installEventFilter(filter)
        
        # set up action menu
        self._menu = QtGui.QMenu()
        self._actions = []
        self.ui.button.setMenu(self._menu)
        self.ui.button.setVisible(False)
        
    def set_actions(self, actions):
        """
        Adds a list of QActions to the actions menu.
        """
        if len(actions) == 0:
            self.ui.button.setVisible(False)
        else:
            self.ui.button.setVisible(True)
            self._actions = actions
            for a in self._actions:
                self._menu.addAction(a)
    
    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not
        """
        p = QtGui.QPalette()
        highlight_col = p.color(QtGui.QPalette.Active, QtGui.QPalette.Highlight)
        
        transp_highlight_str = "rgba(%s, %s, %s, 25%%)" % (highlight_col.red(), highlight_col.green(), highlight_col.blue())
        highlight_str = "rgb(%s, %s, %s)" % (highlight_col.red(), highlight_col.green(), highlight_col.blue())
        
        if selected:
            # make a border around the cell
            self.ui.box.setStyleSheet("""#box {border-width: 2px; 
                                                 border-color: %s; 
                                                 border-style: solid; 
                                                 background-color: %s}
                                      """ % (highlight_str, transp_highlight_str))
        else:
            self.ui.box.setStyleSheet("")
    
    def set_thumbnail(self, pixmap):
        """
        Set a thumbnail given the current pixmap.
        The pixmap must be 512x400 aspect ratio or it will appear squeezed
        """
        self.ui.thumbnail.setPixmap(pixmap)
    
    def set_text(self, header, body):
        """
        Populate three lines of text in the widget
        """
        msg = "<b>%s</b><br>%s" % (header, body)
        self.ui.label.setText(msg)
        self.setToolTip(msg)    

    @staticmethod
    def calculate_size(scale_factor):
        """
        Calculates and returns a suitable size for this widget given a scale factor
        in pixels.
        """        
        # the thumbnail proportions are 512x400
        # add another 34px for the height so the text can be rendered.
        return QtCore.QSize(scale_factor, (scale_factor*0.78125)+34)
        
    def __on_thumb_resized(self):
        """
        Slot Called whenever the thumbnail area is being resized,
        making sure that the label scales with the right aspect ratio.
        """
        new_size = self.ui.thumbnail.size()

        # Aspect ratio of thumbs: 512/400 = 1.28
        calc_height = 0.78125 * (float)(new_size.width())
        
        if abs(calc_height - new_size.height()) > 2: 
            self.ui.thumbnail.resize(new_size.width(), calc_height)


##################################################################################################
# utility classes


class ResizeEventFilter(QtCore.QObject):
    """
    Event filter which emits a resized signal whenever
    the monitored widget resizes
    """
    resized = QtCore.Signal()

    def eventFilter(self, obj, event):
        # peek at the message
        if event.type() == QtCore.QEvent.Resize:
            # re-broadcast any resize events
            self.resized.emit()
        # pass it on!
        return False

