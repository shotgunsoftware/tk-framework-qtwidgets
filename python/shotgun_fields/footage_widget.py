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
Widget that represents the value of a footage field in Shotgun
"""

import math
import re

from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

from sgtk.platform.qt import QtCore, QtGui


class FootageWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a footage field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "footage"

class FootageEditorWidget(QtGui.QLineEdit):

    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "footage"

    editing_finished = QtCore.Signal()

    def setup_widget(self):
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self.editing_finished.emit)
        self.setValidator(_FootageInputValidator())

    def _display_default(self):
        """ Default widget state is empty. """
        self.clear()

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        self.setText(self._string_value(value))

    def _string_value(self, value):
        return str(value)

    def _on_text_changed(self):
        self._value = str(self.text())

class _FootageInputValidator(QtGui.QValidator):

    def fixup(self, input):

        try:
            (feet, frames) = self._get_feet_frames(input)
            input = "%d-%02d" % (feet, frames)
        except ValueError:
            pass

    def validate(self, input, pos):

        try:
            (feet, frames) = self._get_feet_frames(input)
        except ValueError:
            return QtGui.QValidator.Invalid

        return QtGui.QValidator.Acceptable

    def _get_feet_frames(self, input):

        input = input.strip()
        input = input.rstrip("-")

        match = re.match("^\d+$", input)
        if match:
            return divmod(int(match.group(0)), 16)

        match = re.match("^(\d+)-(\d+)$", input)
        if match:
            feet = match.group(1)
            frames = match.group(2)
            (extra_feet, frames) = divmod(int(frames), 16)
            return (int(feet) + extra_feet, frames)

        raise ValueError

