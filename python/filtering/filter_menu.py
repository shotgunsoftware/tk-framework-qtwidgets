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

# shotgun_menus = sgtk.platform.import_framework(
# "tk-framework-qtwidgets", "shotgun_menus"
# )
# ShotgunMenu = shotgun_menus.ShotgunMenu
from ..shotgun_menus import ShotgunMenu


class FilterMenuItemWidget(QtGui.QWidget):
    """
    """

    FILTER_TYPES = {""}

    filter_item_checked = QtCore.Signal(int)
    filter_item_text_changed = QtCore.Signal(str)

    def __init__(self, filter_data, parent=None):
        """
        """

        super(FilterMenuItemWidget, self).__init__(parent)

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
            return LineEditFilterMenuItemWidget(filter_data, parent)

        # Default to choices filter widget
        # if filter_type in (
        # FilterItem.TYPE_STR,
        # FilterItem.TYPE_TEXT
        # ):
        return ChoicesFilterMenuItemWidget(filter_data, parent)

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

        super(FilterMenuItemWidget, self).paintEvent(event)

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.end()


class ChoicesFilterMenuItemWidget(FilterMenuItemWidget):
    """
    """

    def __init__(self, filter_data, parent=None):
        """
        Constructor
        """

        super(ChoicesFilterMenuItemWidget, self).__init__(filter_data, parent)

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


class LineEditFilterMenuItemWidget(FilterMenuItemWidget):
    """
    """

    def __init__(self, filter_data, parent=None):
        super(LineEditFilterMenuItemWidget, self).__init__(filter_data, parent=parent)

        layout = self.layout()

        # name = filter_data.get("display_name", filter_data.get("filter_value"))
        # label = QtGui.QLabel(name)
        # layout.addWidget(label)

        # TODO filter operation may demand a different tyep of filter widget

        self.line_edit = QtGui.QLineEdit()
        self.line_edit.textChanged.connect(self.filter_item_text_changed)
        layout.addWidget(self.line_edit)


class FilterMenu(ShotgunMenu):
    """"""

    filters_changed = QtCore.Signal()

    def __init__(self, filters, parent):
        """
        Constructor
        """

        super(FilterMenu, self).__init__(parent)

        self._group_filters = []

        for filter_group in filters:
            actions = []
            filters = []

            filter_defs = filter_group.get("filters", [])
            if not filter_defs:
                # FIXME handle filter widgets based on type better than this
                if filter_group.get("filter_type") == FilterItem.TYPE_NUMBER:
                    filter_defs.append(
                        {
                            "filter_type": filter_group.get("filter_type"),
                            "filter_op": filter_group.get("filter_op"),
                            "data_func": filter_group.get("data_func"),
                            # "filter_value": filter_value.get("value"),
                            # "display_name": filter_value.get("name", str(filter_name)),
                            # "count": filter_value.get("count", 0)
                        }
                    )

                else:
                    for filter_name, filter_value in filter_group.get(
                        "filter_value", {}
                    ).items():
                        # FIXME
                        filter_defs.append(
                            {
                                "filter_type": filter_group.get("filter_type"),
                                "filter_op": filter_group.get("filter_op"),
                                "data_func": filter_group.get("data_func"),
                                "filter_value": filter_value.get("value"),
                                "display_name": filter_value.get(
                                    "name", str(filter_name)
                                ),
                                "count": filter_value.get("count", 0),
                            }
                        )

            # for filter_def in filter_group.get("filters", []):
            for filter_def in filter_defs:
                filter_item = FilterItem.create(filter_def)

                # name = filter_data.get("display_name", filter_data.get("filter_value"))

                # action = QtGui.QAction(name, parent)
                action = QtGui.QWidgetAction(parent)
                widget = FilterMenuItemWidget.create(filter_def)
                widget.filter_item_checked.connect(
                    lambda state, a=action: self._filter_item_changed(a, state)
                )
                widget.filter_item_text_changed.connect(
                    lambda text, f=filter_item: self._filter_item_text_changed(f, text)
                )
                action.setDefaultWidget(widget)

                action.setCheckable(True)
                action.triggered.connect(
                    lambda checked=False, w=widget: self._filter_changed(w)
                )
                # TODO add init option to set the filter on creation

                filters.append((filter_item, action))
                actions.append(action)

            self._group_filters.append(filters)

            sorted_actions = sorted(actions, key=lambda item: item.text())
            self.add_group(sorted_actions, filter_group.get("name"))

        self._active_filter = FilterItem(
            FilterItem.TYPE_GROUP, FilterItem.OP_AND, filters=[]
        )

    @property
    def active_filter(self):
        """"""

        return self._active_filter

    @property
    def has_filtering(self):
        """
        Return True if the menu has any active filtering.
        """

        return bool(self._active_filter and self._active_filter.filters)

    def _filter_item_changed(self, action, state):
        """
        """

        action.setChecked(state == QtCore.Qt.Checked)
        self._build_filter()
        self.filters_changed.emit()

    def _filter_item_text_changed(self, filter_item, text):
        """
        """

        filter_item.filter_value = text
        # TODO support multiple values via comma separated list
        # filter_item.filter_value = text.split(",")

        self._build_filter()
        self.filters_changed.emit()

    def _filter_changed(self, filter_menu_item_widget):
        """
        Callback on filter action triggered.

        Rebuild the active filter.
        """

        # Update the filter widget
        # FIXME this causes checkbox signal to trigger
        filter_menu_item_widget.action_triggered()

        # FIXME naively just goes through all filters, instead of just modifying the oen that changed
        # self._build_filter()

        # self.filters_changed.emit()

    def _build_filter(self):
        """"""

        active_group_filters = []

        for filters in self._group_filters:
            active_filters = [
                filter_item
                for filter_item, action in filters
                if action.defaultWidget().has_value()
                # if action.isChecked()
            ]
            if active_filters:
                active_group_filters.append(
                    (
                        FilterItem(
                            FilterItem.TYPE_GROUP,
                            FilterItem.OP_OR,
                            filters=active_filters,
                        )
                    )
                )

        self._active_filter.filters = active_group_filters


class ShotgunFilterMenu(FilterMenu):
    """
    Subclass of FilterMenu. The only thing this class does is it builds the filters based on the given
    entity type to the FilterMenu.
    """

    def __init__(self, entity_type, parent):
        """
        """

        filters = self.build_filters(entity_type)
        super(ShotgunFilterMenu, self).__init__(filters, parent)

    @staticmethod
    def build_filters(entity_type):
        """
        """
        # TODO
