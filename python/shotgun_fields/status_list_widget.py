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
Widget that represents the value of a status_list field in Shotgun
"""
import sgtk
from sgtk.platform.qt import QtGui, QtCore
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class StatusListWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a status_list field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "status_list"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: String that is a valid Shotgun status code
        """
        str_val = shotgun_globals.get_status_display_name(value)
        color_str = shotgun_globals.get_status_color(value)

        if color_str:
            # append colored box to indicate status color
            str_val = ("<span style='color: rgb(%s)'>&#9608;</span>&nbsp;%s" % (color_str, str_val))

        return str_val


class StatusListEditorWidget(QtGui.QComboBox):
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "status_list"
    _IMMEDIATE_APPLY = True

    def setup_widget(self):
        self.addItem("")
        self.setMinimumWidth(100)

        valid_values = shotgun_globals.get_valid_values(self._entity_type, self._field_name)
        for value in valid_values:
            self.addItem(shotgun_globals.get_status_display_name(value), value)

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
            self.setCurrentIndex(0)

        display_value = shotgun_globals.get_status_display_name(value)
        index = self.findText(display_value)
        if index != -1:
            self.setCurrentIndex(index)

    def get_value(self):
        return self.itemData(self.currentIndex())

    def _begin_edit(self):
        self.adjustSize()
        self.showPopup()