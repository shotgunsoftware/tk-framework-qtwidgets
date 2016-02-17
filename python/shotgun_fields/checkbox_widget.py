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
Widget that represents the value of a checkbox field in Shotgun
"""
from sgtk.platform.qt import QtCore, QtGui
from .shotgun_field_meta import ShotgunFieldMeta


class CheckBoxWidget(QtGui.QCheckBox):
    """
    Inherited from a :class:`~PySide.QtGui.QCheckBox`, this class is able to
    display a checkbox field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _FIELD_TYPE = "checkbox"

    def _display_default(self):
        """ Default widget state is unchecked. """
        self.setCheckState(QtCore.Qt.Unchecked)

    def _display_value(self, value):
        """
        Take the value as returned by the Shotgun API and display it.

        :param value: The value displayed by the widget
        :type value: Boolean
        """
        if bool(value):
            self.setCheckState(QtCore.Qt.Checked)
        else:
            self.setCheckState(QtCore.Qt.Unchecked)
