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

from sgtk.platform.qt import QtGui, QtCore
from .date_and_time_widget import DateAndTimeWidget
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta


class DateWidget(LabelBaseWidget):

    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "date"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A String representing the date in YYYY-MM-DD form
        """
        if not isinstance(value, datetime.date):
            value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        return self._create_human_readable_date(value)

    def _create_human_readable_date(self, date):
        """
        Return the time represented by the argument as a string where the date portion is
        displayed as "Yesterday", "Today", or "Tomorrow" if appropriate.

        :param date: The date convert to a string
        :type date: :class:`datetime.date`

        :returns: A String representing date appropriate for display
        """

        # get the delta and components
        delta = datetime.date.today() - date

        if delta.days == 1:
            date_str = "Yesterday"
        elif delta.days == 0:
            date_str = "Today"
        elif delta.days == -1:
            date_str = "Tomorrow"
        else:
            # use the date formatting associated with the current locale
            date_str = date.strftime("%x")

        return date_str


class DateEditorWidget(QtGui.QDateEdit):
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "date"

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
        if not isinstance(value, datetime.date):
            value = datetime.datetime.strptime(value, "%Y-%m-%d")
        self.setDate(value)

    def keyPressEvent(self, event):

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
           self.editing_finished.emit()
        else:
            super(DateEditorWidget, self).keyPressEvent(event)

    def get_value(self):

        value = self.date()

        if hasattr(QtCore, "QVariant"):
            # pyqt
            return value.toPyDate()
        else:
            # pyside
            return value.toPython()

