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
    """
    toggle_expanded = QtCore.Signal(bool)    
    
    def set_item(self, model_idx):
        """
        """
        raise NotImplementedError()
        
    def set_expanded(self, expand=True):
        """
        """
        raise NotImplementedError()