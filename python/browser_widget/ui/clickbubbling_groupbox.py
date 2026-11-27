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

class ClickBubblingGroupBox(QtGui.QGroupBox):

    def __init__(self, parent=None):
        QtGui.QGroupBox.__init__(self, parent)

    def mousePressEvent(self, event):
        event.setAccepted(False)

    def mouseDoubleClickEvent(self, event):
        event.setAccepted(False)




