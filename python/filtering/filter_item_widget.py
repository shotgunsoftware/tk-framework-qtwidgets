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
from ..search_widget import SearchWidget


class FilterItemWidget(QtGui.QWidget):
    """
    """

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

        if filter_type in (
            FilterItem.TYPE_NUMBER,
            FilterItem.TYPE_STR,
            FilterItem.TYPE_TEXT,
        ):
            return LineEditFilterItemWidget(filter_data, parent)

        # if filter_type in (FilterItem.TYPE_DATE, FilterItem.TYPE_DATETIME):
        #     return DateTimeFilterItemWidget(filter_data, parent)

        # Default to choices filter widget
        return ChoicesFilterItemWidget(filter_data, parent)

    def has_value(self):
        """
        """
        raise sgtk.TankError("Abstract class method not overriden")

    def action_triggered(self):
        """
        Override this method to provide any functionality.
        """

    def clear_value(self):
        """
        Override this method to provide any functionality.
        """

        raise sgtk.TankError("Abstract class method not overriden")

    def paintEvent(self, event):
        """
        """

        super(FilterItemWidget, self).paintEvent(event)

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.end()


# class DateTimeFilterItemWidget(FilterItem):
#     """
#     """

#     def __init__(self, filter_data, parent=None):
#         """
#         Constructor
#         """

#         super(DateTimeFilterItemWidget, self).__init__(filter_data, parent)


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

    def has_value(self):
        return self.checkbox.isChecked()

    def action_triggered(self):
        """
        """

        # Keep the item checkbox with the action check
        self.checkbox.setChecked(not self.checkbox.isChecked())

    def clear_value(self):
        """
        """

        self.checkbox.setChecked(False)


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

        # self.line_edit = QtGui.QLineEdit()
        self.line_edit = SearchWidget(self)
        # self.line_edit.textChanged.connect(self.filter_item_text_changed)
        self.line_edit.search_edited.connect(self._text_changed)
        layout.addWidget(self.line_edit)

    def has_value(self):
        return self.line_edit.search_text
        # return self.line_edit.text()

    def clear_value(self):
        """
        """

        self.line_edit.clear()
        # self.line_edit._on_clear_clicked()

    def _text_changed(self, text):
        """
        """

        self.filter_item_text_changed.emit(text)
