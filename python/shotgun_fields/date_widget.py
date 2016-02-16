# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Widget that represents the value of a date field in Shotgun
"""
import datetime

from .date_and_time_widget import DateAndTimeWidget


class DateWidget(DateAndTimeWidget):
    """
    Inherited from a :class:`~DateAndTimeWidget`, this class is able to
    display a date field value as returned by the Shotgun API.
    """
    _FIELD_TYPE = "date"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A String representing the date in YYYY-MM-DD form
        """
        dt = datetime.datetime.strptime(value, "%Y-%m-%d")
        return self._create_human_readable_timestamp(dt)
