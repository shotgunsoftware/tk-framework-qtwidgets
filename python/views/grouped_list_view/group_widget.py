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
Default group widget used by the GroupedListView custom view via the
GroupedListViewItemDelegate item delegate.
"""

import sgtk
from sgtk.platform.qt import QtGui, QtCore

from .group_widget_base import GroupWidgetBase
        
class GroupWidget(GroupWidgetBase):
    """
    Default Group widget class
    """
    def __init__(self, parent=None):
        """
        Construction
        
        :param parent:    Parent for this widget
        """
        GroupWidgetBase.__init__(self, parent)

        # create the checkbox that indicates the toggled/expanded state for
        # the group:
        self._cb = QtGui.QCheckBox(self)
        
        # and add it to a basic layout:
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self._cb)
        self.setLayout(layout)
        
        # connect up to the checkbox state-change:
        self._cb.stateChanged.connect(self._on_expand_checkbox_state_changed)
        
    def set_item(self, model_idx):
        """
        Overriden base method used to set the item this widget should be associated 
        with.

        :param model_idx:   The index of the item in the model
        :type model_idx:    :class:`~PySide.QtCore.QModelIndex`
        """
        label = model_idx.data()
        self._cb.setText(label)
        
    def set_expanded(self, expand=True):
        """
        Overriden base method used to set if this widget is expanded or not.
        
        :param expand:  True if the widget should be expanded, False if it
                        should be collapsed.
        """
        self._cb.setCheckState(QtCore.Qt.Checked if expand else QtCore.Qt.Unchecked)
        
    def _on_expand_checkbox_state_changed(self, state):
        """
        Slot signalled when the checkbos state changes - emits the toggle_expanded
        Signal from the base class.
        
        :param state:    The new state of the checkbox
        """
        self.toggle_expanded.emit(state != QtCore.Qt.Unchecked)

