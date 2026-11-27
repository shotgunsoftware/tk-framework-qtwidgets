# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import urllib
import sys

from tank.platform.qt import QtCore, QtGui

from .ui import resources_rc


class ListBase(QtGui.QWidget):

    clicked = QtCore.Signal(QtGui.QWidget)
    double_clicked = QtCore.Signal(QtGui.QWidget)

    def __init__(self, app, worker, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._app = app
        self._worker = worker
        self.ui = self._setup_ui()

    def supports_selection(self):
        return False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # handle this event!
            self.clicked.emit(self)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit(self)

    def set_selected(self, status):
        pass

    def is_selected(self):
        return False

    def set_title(self, title):
        pass

    def set_details(self, text):
        pass

    def get_title(self):
        return None

    def get_details(self):
        return None

    def _setup_ui(self):
        """
        Setup the Qt UI.  Typically, this just instantiates the UI class
        and calls its .setupUi(self) method.

        This can be overriden in child classes - this provides a simple
        mechanism to replace the item UI with a custom version if needed

        :returns:    The constructed QWidget
        """
        raise NotImplementedError()
