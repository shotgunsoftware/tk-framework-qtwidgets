# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from functools import wraps

import sgtk
from sgtk.platform.qt import QtGui, QtCore


def wait_cursor(func):
    """
    Decorator function that overrides the Qt cursor to show the waiting cursor while a function executes.

    :param func: The function to execute
    :type func: function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            response = func(*args, **kwargs)
        finally:
            QtGui.QApplication.restoreOverrideCursor()
        return response

    return wrapper
