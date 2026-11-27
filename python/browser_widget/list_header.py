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
import sys

from tank.platform.qt import QtCore, QtGui
from .ui.header import Ui_Header

from .list_base import ListBase


class ListHeader(ListBase):
    def __init__(self, app, worker, parent=None):
        ListBase.__init__(self, app, worker, parent)

        # initialize line to be plain and the same colour as the text:
        self.ui.line.setFrameShadow(QtGui.QFrame.Plain)
        clr = QtGui.QApplication.palette().text().color()
        self.ui.line.setStyleSheet(
            "#line{color: rgb(%d,%d,%d);}" % (clr.red(), clr.green(), clr.blue())
        )

    def set_title(self, title):
        self.ui.label.setText("<big>%s</big>" % title)

    def get_title(self):
        return self.ui.label.text()

    def _setup_ui(self):
        """
        Setup the Qt UI.  Typically, this just instantiates the UI class
        and calls its .setupUi(self) method.

        :returns:    The constructed QWidget
        """
        ui = Ui_Header()
        ui.setupUi(self)
        return ui
