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
from .ui.list_widget import Ui_ListWidget

class ListWidget(QtGui.QWidget):
    """
    Simple list *item* widget which hosts a square thumbnail, header text
    and body text. It has a fixed size. Multiple of these items are typically
    put together inside a QListView to form a list.
    
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
        self.ui = Ui_ListWidget() 
        self.ui.setupUi(self)
        
        # set up action menu
        self._menu = QtGui.QMenu()   
        self._actions = []             
        self.ui.button.setMenu(self._menu)
        self.ui.button.setVisible(False)
        
    def set_actions(self, actions):
        """
        Adds a list of QActions to add to the actions menu for this widget.
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
        The pixmap must be 100x100 or it will appear squeezed
        """
        self.ui.thumbnail.setPixmap(pixmap)
            
    def set_text(self, header, body):
        """
        Populate the lines of text in the widget
        """
        self.setToolTip("%s<br>%s" % (header, body))        
        self.ui.header_label.setText(header)
        self.ui.body_label.setText(body)

    @staticmethod
    def calculate_size():
        """
        Calculates and returns a suitable size for this widget.
        """        
        return QtCore.QSize(200, 90)

