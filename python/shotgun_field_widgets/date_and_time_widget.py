# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .date_widget import DateWidget
from .shotgun_field_factory import ShotgunFieldFactory


class DateAndTimeWidget(DateWidget):
    def __init__(self, parent=None, value=None):
        DateWidget.__init__(self, parent)

        if value is not None:
            self.setText(self._create_human_readable_timestamp(value, " %I:%M%p"))

ShotgunFieldFactory.register("date_time", DateAndTimeWidget)
