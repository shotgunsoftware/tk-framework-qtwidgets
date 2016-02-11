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
Widget that represents the value of a tag_list field in Shotgun
"""
from sgtk.platform.qt import QtGui
from .shotgun_field_manager import ShotgunFieldManager


class TagsWidget(QtGui.QLabel):
    """
    Inherited from a :class:`~PySide.QtGui.QLabel`, this class is able to
    display a tag_list field value as returned by the Shotgun API.
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
        :type value: A list of strings
        """
        if value is None:
            self.clear()
        else:
            self.setText(", ".join(value))

ShotgunFieldManager.register("tag_list", TagsWidget)
