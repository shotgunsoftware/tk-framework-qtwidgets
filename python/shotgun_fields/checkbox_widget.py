# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui
from .shotgun_field_meta import ShotgunFieldMeta


class CheckBoxWidget(QtGui.QCheckBox):
    """
    Displays a ``checkbox`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "checkbox"
    _EDITOR_TYPE = "checkbox"

    def enable_editing(self, enable):
        """
        Enable or disable editing of the widget.

        This is provided as required for widgets that are used as both editor
        and display.

        :param bool enable: ``True`` to enable, ``False`` to disable
        """
        self.setEnabled(enable)

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self.stateChanged.connect(self._on_state_changed)


    def _display_default(self):
        """
        Display the default value of the widget.
        """
        self.setCheckState(QtCore.Qt.Unchecked)

    def _display_value(self, value):
        """
        Displays the value as returned by the Shotgun API.

        :param bool value: The value displayed by the widget
        """

        # check or uncheck the widget
        if bool(value):
            self.setCheckState(QtCore.Qt.Checked)
        else:
            self.setCheckState(QtCore.Qt.Unchecked)

    def _on_state_changed(self, state):
        """
        Update the stored value as the widget state is changed

        :param int state: Qt enum for check/unchecked
        """

        new_value = (state == QtCore.Qt.Checked)
        if self._value != new_value:
            # set the value internally
            self.set_value(new_value)

