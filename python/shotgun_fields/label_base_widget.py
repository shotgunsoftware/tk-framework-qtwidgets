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
Widget that represents a Shotgun value that can be directly displayed in a QLabel.
"""

import sgtk
from sgtk.platform.qt import QtGui

elided_label = sgtk.platform.current_bundle().import_module("elided_label")


class LabelBaseWidget(QtGui.QLabel):
    """
    Display any Shotgun field value than can be directly rendered as a string.
    """
    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self.setOpenExternalLinks(True)
        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred,
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
        Convert the value to a string for display

        :param value: The value displayed by the widget
        :type value: Anything with a __str__ method
        """
        return str(value)


class ElidedLabelBaseWidget(elided_label.ElidedLabel):
    """
    Display any Shotgun field value than can be directly rendered as a string.
    """
    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self.setOpenExternalLinks(True)

    def _display_default(self):
        """
        Display the default value of the widget.
        """
        self.clear()
        self.setText("")

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        self.setText(self._string_value(value))

    def _string_value(self, value):
        """
        Convert the value to a string for display

        :param value: The value displayed by the widget
        :type value: Anything with a __str__ method
        """
        return str(value)

