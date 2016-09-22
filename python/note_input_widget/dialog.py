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

    The dialog instance will mirror all attributes and methods
    found on the embedded :class:`NoteInputWidget` instance.
    Example::

        note_dialog = NoteInputDialog(parent=self)
        note_dialog.entity_created.connect(self._on_entity_created)
        note_dialog.data_updated.connect(self.rescan)
        note_dialog.set_bg_task_manager(self._task_manager)
        note_dialog.set_current_entity(self._entity_type, self._entity_id)

        # show modal
        note_dialog.exec_()

    """
    def __init__(self, parent):
        """
        :param parent: Qt parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        super(NoteInputDialog, self).__init__(parent)

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
        """
        Attribute dispatcher that promotes all the properties
        and methods of the NoteInputWidget up to the widget.

        :param name: Attribute name to retrieve
        """
        return getattr(self.widget, name)
