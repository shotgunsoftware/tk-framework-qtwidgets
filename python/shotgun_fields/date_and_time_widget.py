# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import datetime
from sgtk.platform.qt import QtGui, QtCore
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta


class DateAndTimeWidget(LabelBaseWidget):
    """
    Display a ``date_time`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "date_time"

    def _create_human_readable_timestamp(self, dt, postfix=""):
        """
        Return the time represented by the argument as a string where the date portion is
        displayed as "Yesterday", "Today", or "Tomorrow" if appropriate.

        By default just the date is displayed, but additional formatting can be appended
        by using the postfix argument.

        :param dt: The date and time to convert to a string
        :type dt: :class:`datetime.datetime`

        :param postfix: What will be displayed after the date portion of the dt argument
        :type postfix: A strftime style :obj:`str`

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
            format = "%x " + postfix

        time_str = dt.strftime(format)
        return time_str

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        self.setText(self._string_value(value))
        self.setToolTip(self._tooltip_value(value, postfix=" %I:%M%p"))

    def _ensure_datetime(self, value):
        """
        Ensures the supplied value is a python datetime object.
        """

        # shotgun_model converts datetimes to floats representing unix time so
        # handle that as a valid value as well
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime.fromtimestamp(value)
        return value

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: :class:`datetime.datetime` or a float representing unix time
        """
        value = self._ensure_datetime(value)

        # return a human readable time format. The postfix formatter used here
        # is '%I:%M%p' which is:
        #
        #   %I = Hour (12-hour clock) as a decimal number [01,12]
        #   %M = Minute as a decimal number [00,59]
        #   %p = Locale's equivalent of either AM or PM
        #
        # resulting in a value like: 01:37AM
        return self._create_human_readable_timestamp(value, postfix=" %I:%M%p")

    def _tooltip_value(self, value, postfix=""):
        """
        Convert the Shotgun value for this field into a tooltip string

        :param value: The value to convert into a string
        :type value: :class:`datetime.datetime` or a float representing unix time
        """
        value = self._ensure_datetime(value)
        return value.strftime("%x" + postfix)


class DateAndTimeEditorWidget(QtGui.QDateTimeEdit):
    """
    Allows editing of a ``date_time`` field value as returned by the Shotgun API.

    Pressing ``Enter`` or ``Return`` when the widget has focus will cause the
    value to be applied and the ``value_changed`` signal to be emitted.
    """
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "date_time"

    # minimum width just to prevent the widget from being too squished
    _MINIMUM_WIDTH = 100

    def get_value(self):
        """
        :return: The internal value being displayed by the widget.
        """
        value = self.dateTime()

        try:
            # pyside
            return value.toPython()
        except AttributeError:
            # pyqt
            return value.toPyDateTime()

    def keyPressEvent(self, event):
        """
        Provides shortcuts for applying modified values.

        :param event: The key press event object
        :type event: :class:`~PySide.QtGui.QKeyEvent`
        """

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.value_changed.emit()
        else:
            super(DateAndTimeEditorWidget, self).keyPressEvent(event)

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self.setCalendarPopup(True)
        self.setMinimumWidth(self._MINIMUM_WIDTH)

    def _display_default(self):
        """
        Display the default value of the widget.
        """
        self.clear()

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        # shotgun_model converts datetimes to floats representing unix time so
        # handle that as a valid value as well
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime.fromtimestamp(value)
        self.setDateTime(value)

