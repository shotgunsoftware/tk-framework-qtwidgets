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
Widget that represents the value of a percent field in Shotgun
"""
import locale

from sgtk.platform.qt import QtGui, QtCore
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta


class PercentWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a percent field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "percent"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: Float or Integer
        """
        return locale.format("%d", value, grouping=True) + "%"

class PercentEditorWidget(QtGui.QSpinBox):

    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "percent"

    def setup_widget(self):
        # SG min/max values for percentages
        self.setMaximum(999)
        self.setMinimum(-999)
        self.setSuffix("%")

    def minimumSizeHint(self):
        return QtCore.QSize(100, 24)

    def _display_default(self):
        """ Default widget state is empty. """
        self.clear()

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        self.setValue(value)

    def keyPressEvent(self, event):

        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
           self.value_changed.emit()
        else:
            super(PercentEditorWidget, self).keyPressEvent(event)

    def get_value(self):
        return self.value()
