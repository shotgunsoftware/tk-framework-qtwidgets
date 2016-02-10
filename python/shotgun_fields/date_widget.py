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

from .date_and_time_widget import DateAndTimeWidget
from .shotgun_field_manager import ShotgunFieldManager


class DateWidget(DateAndTimeWidget):
    def __init__(self, parent=None, value=None, bg_task_manager=None, **kwargs):
        DateAndTimeWidget.__init__(self, parent, **kwargs)
        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.clear()
        else:
            dt = datetime.datetime.strptime(value, "%Y-%m-%d")
            self.setText(self._create_human_readable_timestamp(dt))


ShotgunFieldManager.register("date", DateWidget)
