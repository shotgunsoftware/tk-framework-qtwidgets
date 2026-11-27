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

class ThumbnailLabel(QtGui.QLabel):

    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)

    def setPixmap(self, pixmap):

        # scale the pixmap down to fit
        if pixmap.height() > 55 or pixmap.width() > 80:
            # scale it down to 120x80
            pixmap = pixmap.scaled( QtCore.QSize(80,55),
                                    QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation)




        QtGui.QLabel.setPixmap(self, pixmap)

