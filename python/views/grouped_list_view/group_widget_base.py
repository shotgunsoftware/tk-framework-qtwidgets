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
Base interface for a group widget that will be used in the GroupedListView
custom view
"""

import sgtk
from sgtk.platform.qt import QtGui, QtCore

class GroupWidgetBase(QtGui.QWidget):
    """
    Group widget class
    """
    # signal emitted when the group is expanded/collapsed
    toggle_expanded = QtCore.Signal(bool)# True if expanded, False if collapsed
    
    def set_item(self, model_idx):
        """
        Set the item this widget should be associated with.  This should be 
        implemented in derived classes

        :param model_idx:   The index of the item in the model
        """
        raise NotImplementedError()
        
    def set_expanded(self, expand=True):
        """
        Set if this widget is expanded or not.  This should be implemented 
        in derived classes
        
        :param expand:  True if the widget should be expanded, False if it
                        should be collapsed.
        """
        raise NotImplementedError()