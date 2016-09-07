# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .label_base_widget import ElidedLabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta
from sgtk.platform.qt import QtCore, QtGui


class TextWidget(ElidedLabelBaseWidget):
    """
    Display a ``text`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "text"


class TextEditorWidget(QtGui.QTextEdit):
    """
    Allows editing of a ``text`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "text"

    def get_value(self):
        """
        :return: The internal value being displayed by the widget.
        """
        return self._get_safe_str(self.toPlainText())

    def keyPressEvent(self, event):
        """
        Provides shortcuts for applying modified values.

        :param event: The key press event object
        :type event: :class:`~PySide.QtGui.QKeyEvent`

        Ctrl+Enter or Ctrl+Return will trigger the emission of the ``value_changed``
        signal.
        """
        if event.key() in [
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return
        ] and event.modifiers() & QtCore.Qt.ControlModifier:
            self.value_changed.emit()
            event.ignore()
            return

        super(TextEditorWidget, self).keyPressEvent(event)

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred
        )

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

    def _string_value(self, value):
        """
        Ensure the value to be displayed is a string.

        :param value: The value from Shotgun
        """
        return str(value)

