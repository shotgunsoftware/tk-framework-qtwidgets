# Copyright (c) 2021 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .filter_item import FilterItem
from ..shotgun_menus import ShotgunMenu


class FilterItemWidget(QtGui.QWidget):
    """
    """

    FILTER_TYPES = {""}

    filter_item_checked = QtCore.Signal(int)
    filter_item_text_changed = QtCore.Signal(str)

    def __init__(self, filter_data, parent=None):
        """
        """

        super(FilterItemWidget, self).__init__(parent)

        # Widget style
        # self.setStyleSheet(":hover{background:palette(light)}");

        self.checkbox = None
        self.line_edit = None

        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(layout)

    @classmethod
    def create(cls, filter_data, parent=None):
        """
        """

        filter_type = filter_data.get("filter_type")
        if not filter_type:
            raise sgtk.TankError("Missing required filter type.")

        if filter_type in (FilterItem.TYPE_NUMBER):
            return LineEditFilterItemWidget(filter_data, parent)

        # Default to choices filter widget
        # if filter_type in (
        # FilterItem.TYPE_STR,
        # FilterItem.TYPE_TEXT
        # ):
        return ChoicesFilterItemWidget(filter_data, parent)

    def has_value(self):
        """
        """

        if self.checkbox and self.checkbox.isChecked():
            return True

        if self.line_edit and self.line_edit.text():
            return True

        return False

    def action_triggered(self):
        """
        """

        if self.checkbox:
            self.checkbox.setChecked(not self.checkbox.isChecked())

    def paintEvent(self, event):
        """
        """

        super(FilterItemWidget, self).paintEvent(event)

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.end()


class ChoicesFilterItemWidget(FilterItemWidget):
    """
    """

    def __init__(self, filter_data, parent=None):
        """
        Constructor
        """

        super(ChoicesFilterItemWidget, self).__init__(filter_data, parent)

        layout = self.layout()

        self.checkbox = QtGui.QCheckBox()
        self.checkbox.stateChanged.connect(self.filter_item_checked)
        layout.addWidget(self.checkbox)

        icon = filter_data.get("icon")
        if icon:
            icon_label = QtGui.QLabel()
            icon_label.setPixmap(icon.pixmap(14))
            layout.addWidget(icon_label)

        name = filter_data.get("display_name", filter_data.get("filter_value"))
        label = QtGui.QLabel(name)
        layout.addWidget(label)

        count = filter_data.get("count")
        if count:
            count_label = QtGui.QLabel()
            count_label.setText(str(count))
            layout.addStretch()
            layout.addWidget(count_label)


class LineEditFilterItemWidget(FilterItemWidget):
    """
    """

    def __init__(self, filter_data, parent=None):
        super(LineEditFilterItemWidget, self).__init__(filter_data, parent=parent)

        layout = self.layout()

        # name = filter_data.get("display_name", filter_data.get("filter_value"))
        # label = QtGui.QLabel(name)
        # layout.addWidget(label)

        # TODO filter operation may demand a different tyep of filter widget

        self.line_edit = QtGui.QLineEdit()
        self.line_edit.textChanged.connect(self.filter_item_text_changed)
        layout.addWidget(self.line_edit)
