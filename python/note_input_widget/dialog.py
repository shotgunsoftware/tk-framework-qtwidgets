# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui
from . import NoteInputWidget

class NoteInputDialog(QtGui.QDialog):
    """
    A dialog wrapper for the :class:`NoteInputWidget` widget.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super(NoteInputDialog, self).__init__(*args, **kwargs)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.widget = NoteInputWidget(None)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(3,3,3,3)
        self.layout.addWidget(QtGui.QLabel("Please enter a new note:"))
        self.layout.addWidget(self.widget)
        self.setLayout(self.layout)

        self.widget.entity_created.connect(self.accept)
        self.widget.close_clicked.connect(self.reject)

        self.widget.open_editor()

    def __getattr__(self, name):
        return getattr(self.widget, name)
