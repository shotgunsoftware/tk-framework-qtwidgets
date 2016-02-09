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

from .shotgun_field_factory import ShotgunFieldFactory


class DateWidget(QtGui.QLabel):
    def __init__(self, parent=None, value=None):
        QtGui.QLabel.__init__(self, parent)

        if value is not None:
            date_obj = datetime.datetime.strptime(value, "%Y-%m-%d")
            self.setText(self._create_human_readable_timestamp(date_obj))

    def _create_human_readable_timestamp(self, datetime_obj, postfix=""):
        # get the delta and components
        delta = datetime.datetime.now(datetime_obj.tzinfo) - datetime_obj

        if delta.days == 1:
            format = "Yesterday%s" % postfix
        elif delta.days == 0:
            format = "Today%s" % postfix
        elif delta.days == -1:
            format = "Tomorrow%s" % postfix
        else:
            format = "%%x%s" % postfix

        time_str = datetime_obj.strftime(format)
        return time_str

ShotgunFieldFactory.register("date", DateWidget)
