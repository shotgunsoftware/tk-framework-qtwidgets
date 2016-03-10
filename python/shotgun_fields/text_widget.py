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
Widget that represents the value of a text field in Shotgun
"""
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

from sgtk.platform.qt import QtCore, QtGui


class TextWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a text field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "text"


class TextEditorWidget(QtGui.QLineEdit):
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "text"

    def setup_widget(self):
        self.textChanged.connect(self._on_text_changed)

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
