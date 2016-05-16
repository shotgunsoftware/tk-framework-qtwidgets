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


class DateWidget(LabelBaseWidget):
    """
    Display a ``date`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "date"

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

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A String representing the date in YYYY-MM-DD form
        """
        if not isinstance(value, datetime.date):
            value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        return self._create_human_readable_date(value)


class DateEditorWidget(QtGui.QDateEdit):
    """
    Allows editing of a ``date`` field value as returned by the Shotgun API.

    Pressing ``Enter`` or ``Return`` when the widget has focus will cause the
    value to be applied and the ``value_changed`` signal to be emitted.
    """
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "date"

    def get_value(self):
        """
        :return: The internal value being displayed by the widget.
        """
        value = self.date()

        if hasattr(QtCore, "QVariant"):
            # pyqt
            return value.toPyDate()
        else:
            # pyside
            return value.toPython()

    def keyPressEvent(self, event):
        """
        Provides shortcuts for applying modified values.

        :param event: The key press event object
        :type event: :class:`~PySide.QtGui.QKeyEvent`
        """
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.value_changed.emit()
        else:
            super(DateEditorWidget, self).keyPressEvent(event)

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self.setCalendarPopup(True)
        self.setMinimumWidth(100)

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
        if not isinstance(value, datetime.date):
            value = datetime.datetime.strptime(value, "%Y-%m-%d")
        self.setDate(value)

