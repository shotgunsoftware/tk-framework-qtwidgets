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
Widget that represents the value of a date_time field in Shotgun
"""
import datetime
from sgtk.platform.qt import QtGui, QtCore
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta


class DateAndTimeWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a date_time field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "date_time"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: :class:`datetime.datetime` or a float representing unix time
        """
        # shotgun_model converts datetimes to floats representing unix time so
        # handle that as a valid value as well
        if isinstance(value, float):
            value = datetime.datetime.fromtimestamp(value)
        return self._create_human_readable_timestamp(value, " %I:%M%p")

    def _create_human_readable_timestamp(self, dt, postfix=""):
        """
        Return the time represented by the argument as a string where the date portion is
        displayed as "Yesterday", "Today", or "Tomorrow" if appropriate.

        By default just the date is displayed, but additional formatting can be appended
        by using the postfix argument.

        :param dt: The date and time to convert to a string
        :type dt: :class:`datetime.datetime`

        :param postfix: What will be displayed after the date portion of the dt argument
        :type postfix: A strftime style String

        :returns: A String representing dt appropriate for display
        """
        # get the delta and components
        delta = datetime.datetime.now(dt.tzinfo) - dt

        if delta.days == 1:
            format = "Yesterday%s" % postfix
        elif delta.days == 0:
            format = "Today%s" % postfix
        elif delta.days == -1:
            format = "Tomorrow%s" % postfix
        else:
            # use the date formatting associated with the current locale
            format = "%%x%s" % postfix

        time_str = dt.strftime(format)
        return time_str


class DateAndTimeEditorWidget(QtGui.QDateTimeEdit):
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "date_time"

    editing_finished = QtCore.Signal()

    def setup_widget(self):
        self.setCalendarPopup(True)
        self.setMinimumWidth(100)

    def _display_default(self):
        """ Default widget state is empty. """
        self.clear()

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        # shotgun_model converts datetimes to floats representing unix time so
        # handle that as a valid value as well
        if isinstance(value, float):
            value = datetime.datetime.fromtimestamp(value)
        self.setDateTime(value)

    def keyPressEvent(self, event):

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
           self.editing_finished.emit()
        else:
            super(DateAndTimeEditorWidget, self).keyPressEvent(event)

