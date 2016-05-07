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
Widget that represents the value of a list field in Shotgun
"""
import sgtk
from sgtk.platform.qt import QtGui, QtCore
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class ListWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a list field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "list"


class ListEditorWidget(QtGui.QComboBox):
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "list"
    _IMMEDIATE_APPLY = True

    def setup_widget(self):
        self.addItem("")
        valid_values = shotgun_globals.get_valid_values(self._entity_type, self._field_name)
        self.addItems(valid_values)

        self.activated.connect(
            lambda i: self.value_changed.emit()
        )

    def _display_default(self):
        """ Default widget state is empty. """
        self.setCurrentIndex(0)

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        if value is None:
            self.clearEditText()

        index = self.findText(value)
        if index != -1:
            self.setCurrentIndex(index)

    def get_value(self):
        return self.currentText()

    def _begin_edit(self):
        self.showPopup()
