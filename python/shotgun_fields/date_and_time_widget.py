# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import datetime
from sgtk.platform.qt import QtGui

from .shotgun_field_manager import ShotgunFieldManager


class DateAndTimeWidget(QtGui.QLabel):
    def __init__(self, parent=None, value=None, bg_task_manager=None, **kwargs):
        QtGui.QLabel.__init__(self, parent, **kwargs)
        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.clear()
        else:
            self.setText(self._create_human_readable_timestamp(value, " %I:%M%p"))

    def _create_human_readable_timestamp(self, dt, postfix=""):
        # get the delta and components
        delta = datetime.datetime.now(dt.tzinfo) - dt

        if delta.days == 1:
            format = "Yesterday%s" % postfix
        elif delta.days == 0:
            format = "Today%s" % postfix
        elif delta.days == -1:
            format = "Tomorrow%s" % postfix
        else:
            format = "%%x%s" % postfix

        time_str = dt.strftime(format)
        return time_str

ShotgunFieldManager.register("date_time", DateAndTimeWidget)
