# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import locale
from sgtk.platform.qt import QtGui
from .shotgun_field_manager import ShotgunFieldManager


class NumberWidget(QtGui.QLabel):
    def __init__(self, parent=None, value=None, bg_task_manager=None, **kwargs):
        QtGui.QLabel.__init__(self, parent, **kwargs)
        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.clear()
        else:
            self.setText(locale.format("%d", value, grouping=True))

ShotgunFieldManager.register("number", NumberWidget)
