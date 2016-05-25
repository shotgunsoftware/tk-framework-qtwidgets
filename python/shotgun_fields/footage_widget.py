# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import re

from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

from sgtk.platform.qt import QtCore, QtGui


class FootageWidget(LabelBaseWidget):
    """
    Display a ``footage`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "footage"

class FootageEditorWidget(QtGui.QLineEdit):
    """
    Allows editing of a ``footage`` field value as returned by the Shotgun API.

    Pressing ``Enter`` or ``Return`` when the widget has focus will cause the
    value to be applied and the ``value_changed`` signal to be emitted.
    """
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "footage"

    def get_value(self):
        """
        :return: The internal value being displayed by the widget.
        """
        return self.validator().fixup(self.text())

    def keyPressEvent(self, event):
        """
        Provides shortcuts for applying modified values.

        :param event: The key press event object
        :type event: :class:`~PySide.QtGui.QKeyEvent`
        """
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.value_changed.emit()
        else:
            super(FootageEditorWidget, self).keyPressEvent(event)

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self.setMinimumWidth(100)
        self.setValidator(_FootageInputValidator())

        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self.value_changed.emit)

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
        self.setText(self._string_value(value))

    def _on_text_changed(self):
        """
        Keep the internal value updated as the user types
        """
        self._value = str(self.text())

    def _string_value(self, value):
        """
        Ensure the value to be displayed is a string.

        :param value: The value from Shotgun
        """
        return str(value)


class _FootageInputValidator(QtGui.QValidator):
    """
    A validator for the {feet}-{frames} footage spec.
    """

    def fixup(self, input_str):
        """
        Translate the input string into a valid string if possible.

        :param str input_str: The input value to translate.

        :return: The translated value or the original input string if translation is
            not possible.
        """
        try:
            # translate the input into feet & frames
            (feet, frames) = self._get_feet_frames(input_str)
            input_str = "%d-%02d" % (feet, frames)
        except ValueError:
            pass

        return input_str

    def validate(self, input_str, pos):
        """
        Validate the input_str string if it is possible to infer feet and frames.

        :param input_str: The input string
        :param pos: The cursor position within the widget

        :return: :class:`~PySide.QtGui.QValidator` enum ``Invalid`` or ``Acceptable``
            depending on if the input string is valid.
        :rtype: int
        """
        try:
            (feet, frames) = self._get_feet_frames(input_str)
        except ValueError:
            return QtGui.QValidator.Invalid

        return QtGui.QValidator.Acceptable

    def _get_feet_frames(self, input_str):
        """
        Convert the input string into a tuple representing ``feet`` and ``frames``.

        :param str input_str: A string representing a footage spec.
        :return: A tuple of the form ``(feet, frames)`` inferred from the input
            string.
        :rtype tuple:

        :raises: ``ValueError`` if feet and frames cannot be inferred.
        """

        input_str = str(input_str)
        input_str = input_str.strip()
        input_str = input_str.rstrip("-")

        if str.isdigit(input_str):
            # if the value is simply an integer, we can calculate the number of
            # feet (16 frames per foot) and the remaining frames using ``divmod``.
            return divmod(int(input_str), 16)

        match = re.match("^(\d+)-(\d+)$", input_str)
        if match:
            # the input value is of the form ``{feet}-{frames}``. ensure the
            # frames value is reduced, then compute the total feet and frames.
            feet = match.group(1)
            frames = match.group(2)
            (extra_feet, frames) = divmod(int(frames), 16)
            return (int(feet) + extra_feet, frames)

        raise ValueError

