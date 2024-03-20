# Copyright (c) 2021 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from tank_vendor import six

search_widget = sgtk.platform.current_bundle().import_module("search_widget")
shotgun_search_widget = sgtk.platform.current_bundle().import_module(
    "shotgun_search_widget"
)


class FilterItemWidget(QtGui.QWidget):
    """
    Abstract widget class to represent a FilterItem object. This widget can be used to insert custom
    widgets into the FilterMenu actions.
    """

    # Signal emitted when the filter widget's checkbox state changed.
    state_changed = QtCore.Signal(QtCore.Qt.CheckState)
    # Signal emitted when the filter widget's value changed.
    value_changed = QtCore.Signal(object)

    def __init__(
        self, filter_id, group_id, parent=None, bg_task_manager=None, filter_data=None
    ):
        """
        Constructor. Set up the widget.

        :param filter_id: The unique identifier for this widget.
        :type filter_id: str
        :param group_id: The unique identifier for the group this widget belongs to.
        :type group_id: str
        :param parent: The widget's parent
        :type parent: :class:`sgtk.platform.qt.QWidget`
        :param bg_task_manager: An instance of a Background Task Manager used by the search widget.
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        :param filter_data: Optional filter data to create the filter item with.
        :type filter_data: dict
        """

        super(FilterItemWidget, self).__init__(parent)

        self._id = filter_id
        self._group_id = group_id
        self._bg_task_manager = bg_task_manager

        filter_data = filter_data or {}
        self._display_name = filter_data.get("display_name", "")
        self._raw_value = filter_data.get("filter_value")

        # Enable mouse tracking for hover events.
        self.setMouseTracking(True)

    def __repr__(self):
        """Return string representation of the FilterItemWidget."""

        params = {
            "id": self.id,
            "field": self.group_id,
        }
        params_str = ", ".join(
            ["{}={}".format(key, value) for key, value in params.items()]
        )

        return "<{class_name} {params}>".format(
            class_name=self.__class__.__name__, params=params_str
        )

    @property
    def id(self):
        """Get the unique id for this widget."""
        return self._id

    @property
    def group_id(self):
        """Get the unique id for the group this widget belongs to."""
        return self._group_id

    @property
    def name(self):
        """Return the dispaly text for this widget."""
        return self._display_name

    @property
    def value(self):
        """Get or set the widget's value."""
        raise sgtk.TankError("Abstract class method not overriden")

    @value.setter
    def value(self, value):
        raise sgtk.TankError("Abstract class method not overriden")

    @property
    def sort_value(self):
        """Get the widget's value that is sortable."""
        # First try to extract the sort value from the raw value.
        value = self._raw_value
        if isinstance(value, dict):
            value = value.get("name")
        # Default to the display name if the raw value is not sortable.
        if value is None:
            value = self.name
        # Sanitize the value as needed based on value type
        if isinstance(value, six.string_types):
            return value.lower()
        return value

    def set_value(self, value):
        """Convenience method to set the value for callback."""
        self.value = value

    def has_value(self):
        """Return True if the widget has a value, else False."""
        raise sgtk.TankError("Abstract class method not overriden")

    def clear_value(self):
        """Clear the widget's current value."""
        raise sgtk.TankError("Abstract class method not overriden")

    def restore(self, state):
        """
        Restore the widget to the provided state.

        :param state: The state to restore the widget from.
        :type state: any
        """
        raise sgtk.TankError("Abstract class method not overriden")


class ChoicesFilterItemWidget(FilterItemWidget):
    """
    A widget to represent a filter item that belongs to group of choices.
    """

    def __init__(
        self, filter_id, group_id, filter_data, parent=None, bg_task_manager=None
    ):
        """
        Constructor.

        Initialize the widget UI:
          - Left aligned checkbox
          - Left aligned icon (optional)
          - Left aligned filter value display text
          - Right aligned filter value count

        :param filter_id: The unique identifier for this widget.
        :type filter_id: str
        :param group_id: The unique identifier for the group this widget belongs to.
        :type group_id: str
        :param filter_data: Additional data to initialize the widget.
        :type filter_data: dict
        :param parent: The widget's parent
        :type parent: :class:`sgtk.platform.qt.QWidget`
        :param bg_task_manager: An instance of a Background Task Manager used by the search widget.
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """

        super(ChoicesFilterItemWidget, self).__init__(
            filter_id,
            group_id,
            parent=parent,
            bg_task_manager=bg_task_manager,
            filter_data=filter_data,
        )

        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        # Left-aligned checkbox
        self.checkbox = QtGui.QCheckBox()

        def __on_state_changed(state):
            if isinstance(state, int):
                state = QtCore.Qt.CheckState(state)
            self.state_changed.emit(state)

        self.checkbox.stateChanged.connect(__on_state_changed)
        layout.addWidget(self.checkbox)

        # Left-aligned (optional) icon
        icon = filter_data.get("icon")
        if icon:
            icon_label = QtGui.QLabel()
            icon_label.setPixmap(icon.pixmap(14))
            layout.addWidget(icon_label)

        # Left-aligned filter value display text
        name = six.ensure_str(self._display_name)
        self.label = QtGui.QLabel(name)
        layout.addWidget(self.label)

        # Right-aligned count label
        count = filter_data.get("count")
        if count:
            self.count_label = QtGui.QLabel(str(count))
        else:
            self.count_label = QtGui.QLabel()
        layout.addStretch()
        layout.addWidget(self.count_label)

        self.setLayout(layout)

    def paintEvent(self, event):
        """
        Override the Qt method.

        Highlight the background color on mouse hover.
        """

        super(ChoicesFilterItemWidget, self).paintEvent(event)

        option = QtGui.QStyleOption()
        option.initFrom(self)
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            if option.state & QtGui.QStyle.State_MouseOver:
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                hover_color = option.palette.highlight().color()
                painter.setBrush(QtGui.QBrush(hover_color))
                painter.setPen(QtGui.QPen(hover_color))
                painter.drawRect(
                    0, 0, painter.device().width(), painter.device().height()
                )
        finally:
            painter.end()

    @FilterItemWidget.name.getter
    def name(self):
        """
        Get the name of the choices filter item.

        The name of this widget is used for the label text, which is the display name.
        """
        return self.label.text()

    @FilterItemWidget.value.getter
    def value(self):
        """
        Get or set the value of the choices filter item widget.

        The value of this widget represents whether or not the widget is checked.
        """
        return self.checkbox.isChecked()

    @value.setter
    def value(self, value):
        if isinstance(value, bool):
            self.checkbox.setChecked(value)

        elif isinstance(value, dict):
            if "count" in value:
                self.count_label.setText(str(value["count"]))
                self.count_label.update()

            if "checked" in value:
                self.value = value["checked"]

        else:
            assert (
                False
            ), "Attempting to set ChoicesFilterItemWidget value with invalid data"

    def has_value(self):
        """Return True if the widget's checkbox is checked, else False."""
        return self.value

    def clear_value(self):
        """Clear the widget's value by unchecking the widget's checkbox."""
        self.value = False

    def restore(self, state):
        """
        Restore the widget's checkbox state.

        :param state: The state to restore the widget from.
        :type state: bool | ChoicesFilterItemWidget
        """

        if isinstance(state, ChoicesFilterItemWidget):
            self.value = state.value

        elif isinstance(state, bool):
            self.value = state

        else:
            assert (
                False
            ), "Cannot restore ChoicesFilterItemWidget state from '{}'".format(state)


class SearchFilterItemWidget(FilterItemWidget):
    """
    A filter widget for searching text values. Reuses the SearchWidget class.
    """

    def __init__(
        self, filter_id, group_id, filter_data, parent=None, bg_task_manager=None
    ):
        """
        Constructor.

        Initialize the widget UI:
          - Add a search widget according to the field type.
          If we are dealing with an PTR entity/multi-entity field, add a GlobalSearchWidget
          otherwise, add a SearchWidget.

        :param filter_id: The unique identifier for this widget.
        :type filter_id: str
        :param group_id: The unique identifier for the group this widget belongs to.
        :type group_id: str
        :param filter_data: Additional data to initialize the widget.
        :type filter_data: dict
        :param parent: The widget's parent
        :type parent: :class:`sgtk.platform.qt.QWidget`
        :param bg_task_manager: An instance of a Background Task Manager used by the search widget.
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """

        super(SearchFilterItemWidget, self).__init__(
            filter_id,
            group_id,
            parent=parent,
            bg_task_manager=bg_task_manager,
            filter_data=filter_data,
        )

        self._value = ""

        short_name = filter_data.get("short_name", self.name)
        sg_data = filter_data.get("sg_data", {})

        # in case we are dealing with an PTR entity/multi-entity field and the widget has been initialized
        # using a BackgroundTaskManager, use a GlobalSearchWidget to help the user find the right entity to pick
        if (
            sg_data
            and sg_data.get("data_type") in ["entity", "multi_entity"]
            and self._bg_task_manager
        ):
            self.line_edit = shotgun_search_widget.GlobalSearchWidget(self)
            self.line_edit.set_bg_task_manager(self._bg_task_manager)
            searchable_entities = {}
            for entity_type in sg_data.get("valid_types"):
                searchable_entities[entity_type] = []
            self.line_edit.set_searchable_entity_types(searchable_entities)
            self.line_edit.entity_activated.connect(
                lambda entity_type, entity_id, entity_name: self.set_value(
                    {"type": entity_type, "name": entity_name, "id": entity_id}
                )
            )

        else:
            self.line_edit = search_widget.SearchWidget(self)
            self.line_edit.search_changed.connect(self.set_value)

        if self.name:
            self.line_edit.set_placeholder_text("Enter {}".format(short_name))
        self.line_edit.setToolTip("Press Enter to search by {}.".format(self.name))

        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    @FilterItemWidget.value.getter
    def value(self):
        """Return the search widget's value."""
        return self._value

    @value.setter
    def value(self, value):
        """
        Set the search widget's value.

        :param value: The value to set.
        :type value: any
        """
        self._value = value
        self.value_changed.emit(value)

    def has_value(self):
        """Return True if the search widget has a value, else False."""
        return bool(self.value)

    def clear_value(self):
        """Clear the search widget's value."""
        self.value = ""
