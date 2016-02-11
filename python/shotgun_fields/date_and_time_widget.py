# Copyright (c) 2015 Shotgun Software Inc.
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
from sgtk.platform.qt import QtGui

from .shotgun_field_manager import ShotgunFieldManager


class DateAndTimeWidget(QtGui.QLabel):
    """
    Inherited from a :class:`~PySide.QtGui.QLabel`, this class is able to
    display a date_time field value as returned by the Shotgun API.
    """

    def __init__(self, parent=None, value=None, bg_task_manager=None, **kwargs):
        """
        Constructor for the widget.  This method passes all keyword args except
        for those below through to the :class:`~PySide.QtGui.QLabel` it
        subclasses.

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :param value: The initial value displayed by the widget as described by set_value

        :param bg_task_manager: The task manager the widget will use if it needs to run a task
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        QtGui.QLabel.__init__(self, parent, **kwargs)
        self.set_value(value)

    def set_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value displayed by the widget
        :type value: :class:`~datetime.datetime`
        """
        if value is None:
            self.clear()
        else:
            self.setText(self._create_human_readable_timestamp(value, " %I:%M%p"))

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
            format = "%%x%s" % postfix

        time_str = dt.strftime(format)
        return time_str

ShotgunFieldManager.register("date_time", DateAndTimeWidget)
