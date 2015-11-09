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
from sgtk.platform.qt import QtGui, QtCore

class GroupWidgetBase(QtGui.QWidget):
    """
    Base interface for a group widget that will be used in the
    :class:`GroupedListView` custom view
    
    :signal toggle_expanded(bool): Emitted when the group's expansion
                             state is toggled. Includes a boolean
                             to indicate if the group is expanded or not.
    
    """
    # True if expanded, False if collapsed
    toggle_expanded = QtCore.Signal(bool)
    
    def set_item(self, model_idx):
        """
        Set the item this widget should be associated with.  This should be 
        implemented in derived classes

        :param model_idx:   The index of the item in the model
        :type model_index:  :class:`~PySide.QtCore.QModelIndex`
        """
        raise NotImplementedError()
        
    def set_expanded(self, expand=True):
        """
        Set if this widget is expanded or not.  This should be implemented 
        in derived classes
        
        :param expand:  True if the widget should be expanded, False if it
                        should be collapsed.
        :type expand:   bool
        """
        raise NotImplementedError()
