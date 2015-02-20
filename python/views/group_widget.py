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

from .group_widget_base import GroupWidgetBase
        
class GroupWidget(GroupWidgetBase):
    """
    """
    toggle_expanded = QtCore.Signal(bool)

    def __init__(self, parent=None):
        """
        """
        GroupWidgetBase.__init__(self, parent)

        # create the checkbox that indicates the toggled/expanded state for
        # the group:
        self._cb = QtGui.QCheckBox(self)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self._cb)
        self.setLayout(layout)
        
        # connect up to the checkbox state-change:
        self._cb.stateChanged.connect(self._on_expand_checkbox_state_changed)
        
    def set_item(self, model_idx):
        """
        """
        label = model_idx.data()
        self._cb.setText(label)
        
    def set_expanded(self, expand=True):
        """
        """
        self._cb.setCheckState(QtCore.Qt.Checked if expand else QtCore.Qt.Unchecked)
        
    def _on_expand_checkbox_state_changed(self, state):
        """
        """
        self.toggle_expanded.emit(state != QtCore.Qt.Unchecked)