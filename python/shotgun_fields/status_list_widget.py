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
Widget that represents the value of a status_list field in Shotgun
"""
import sgtk
from sgtk.platform.qt import QtGui
from .shotgun_field_manager import ShotgunFieldManager

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class StatusListWidget(QtGui.QLabel):
    """
    Inherited from a :class:`~PySide.QtGui.QLabel`, this class is able to
    display a status_list field value as returned by the Shotgun API.
    """

    def __init__(self, parent=None, entity=None, field_name=None, bg_task_manager=None, **kwargs):
        """
        Constructor for the widget.  This method passes all keyword args except
        for those below through to the :class:`~PySide.QtGui.QLabel` it
        subclasses.

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field

        :param field_name: Shotgun field name
        :type field_name: String

        :param bg_task_manager: The task manager the widget will use if it needs to run a task
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        QtGui.QLabel.__init__(self, parent, **kwargs)
        self.set_value(entity[field_name])

    def set_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value displayed by the widget
        :type value: A valid Shotgun status String
        """
        if value is None:
            self.clear()
        else:
            str_val = shotgun_globals.get_status_display_name(value)
            color_str = shotgun_globals.get_status_color(value)

            if color_str:
                # append colored box to indicate status color
                str_val = ("<span style='color: rgb(%s)'>&#9608;</span>&nbsp;%s" % (color_str, str_val))

            self.setText(str_val)

ShotgunFieldManager.register("status_list", StatusListWidget)
