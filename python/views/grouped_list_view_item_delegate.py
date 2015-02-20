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

from .widget_delegate import WidgetDelegate
from .group_widget import GroupWidget

class GroupedListViewItemDelegate(WidgetDelegate):
    """
    """
    def __init__(self, view):
        """
        """
        WidgetDelegate.__init__(self, view)
        
        self._calc_group_widget = None
        
    def create_group_widget(self, parent):
        """
        """
        return GroupWidget(parent)
    
    def sizeHint(self, style_options, model_index):
        """
        """
        if model_index.parent() == self.view.rootIndex():
            expanded = self.view.is_expanded(model_index)
            
            # the index is a root/group item:
            if not self._calc_group_widget:
                self._calc_group_widget = self.create_group_widget(self.view)
                self._calc_group_widget.setVisible(False)
                                
            self._calc_group_widget.set_expanded(expanded)
            self._calc_group_widget.set_item(model_index)
            layout = self._calc_group_widget.layout()
            if layout:
                layout.invalidate()
                layout.activate()

            return self._calc_group_widget.sizeHint()
        else:
            # return the base size hint:
            return WidgetDelegate.sizeHint(self, style_options, model_index)        