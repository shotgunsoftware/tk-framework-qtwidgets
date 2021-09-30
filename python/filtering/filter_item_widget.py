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


class FilterItemWidget(QtGui.QWidget):
    """
    Abstract widget class to represent a FilterItem object. This widget can be used to insert custom
    widgets into the FilterMenu actions.
    """

    # Signal emitted when the filter widget's checkbox state changed.
    state_changed = QtCore.Signal(int)
    # Signal emitted when the filter widget's value changed.
    value_changed = QtCore.Signal(object)

    def __init__(self, filter_id, group_id, parent=None):
        """
        Constructor. Set up the widget.

        :param filter_id: The unique identifier for this widget.
        :type filter_id: str
        :param group_id: The unique identifier for the group this widget belongs to.
        :type group_id: str
        :param parent: The widget's parent
        :type parent: :class:`sgtk.platform.qt.QWidget`
        """

        super(FilterItemWidget, self).__init__(parent)

        self._id = filter_id
        self._group_id = group_id

        # Enabel mouse tracking for hover events.
        self.setMouseTracking(True)

    def __repr__(self):
        """
        Return string representation of the FilterItemWidget.
        """

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
        """
        Get the unique id for this widget.
        """

        return self._id

    @property
    def group_id(self):
        """
        Get the unique id for the group this widget belongs to.
        """

        return self._group_id

    @property
    def name(self):
        """
        Return the dispaly text for this widget.
        """

        raise sgtk.TankError("Abstract class method not overriden")

    @property
    def value(self):
        """
        Return the widget's current value.
        """

        raise sgtk.TankError("Abstract class method not overriden")

    @value.setter
    def value(self, value):
        """
        Set the widget's value.

        :param value: The value to set the widget's value to.
        :type value: any
        """

        raise sgtk.TankError("Abstract class method not overriden")

    def set_value(self, value):
        """
        Convenience method to set the value for callback.
        """

        self.value = value

    def has_value(self):
        """
        Return True if the widget has a value, else False.
        """

        raise sgtk.TankError("Abstract class method not overriden")

    def clear_value(self):
        """
        Clear the widget's current value.
        """

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

    def __init__(self, filter_id, group_id, filter_data, parent=None):
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
        """

        super(ChoicesFilterItemWidget, self).__init__(filter_id, group_id, parent)

        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        # Left-aligned checkbox
        self.checkbox = QtGui.QCheckBox()
        self.checkbox.stateChanged.connect(self.state_changed)
        layout.addWidget(self.checkbox)

        # Left-aligned (optional) icon
        icon = filter_data.get("icon")
        if icon:
            icon_label = QtGui.QLabel()
            icon_label.setPixmap(icon.pixmap(14))
            layout.addWidget(icon_label)

        # Left-aligned filter value display text
        name = six.ensure_str(
            filter_data.get("display_name", filter_data.get("filter_value"))
        )
        self.label = QtGui.QLabel(name)
        layout.addWidget(self.label)

        # Right-aligned count label
        count = filter_data.get("count")
        if count:
            self.count_label = QtGui.QLabel(str(count))
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
        Return the widget's label text, this is the display name for this widget.
        """

        return self.label.text()

    @FilterItemWidget.value.getter
    def value(self):
        """
        Return whether or not the widget's checkbox is checked.
        """

        return self.checkbox.isChecked()

    @value.setter
    def value(self, value):
        """
        Set the widget's value by checking or unchecking the widget's checkbox based on the value.

        :param value: True to check the widget's checkbox, else False.
        :type value: bool
        """

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
        """
        Return True if the widget's checkbox is checked, else False.
        """

        return self.value

    def clear_value(self):
        """
        Clear the widget's value by unchecking the widget's checkbox.
        """

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


class TextFilterItemWidget(FilterItemWidget):
    """
    A filter widget for searching text values. Reuses the SearchWidget class.
    """

    def __init__(self, filter_id, group_id, filter_data, parent=None):
        """
        Constructor.

        Initialize the widget UI:
          - Add a SearchWidget

        :param filter_id: The unique identifier for this widget.
        :type filter_id: str
        :param group_id: The unique identifier for the group this widget belongs to.
        :type group_id: str
        :param filter_data: Additional data to initialize the widget.
        :type filter_data: dict
        :param parent: The widget's parent
        :type parent: :class:`sgtk.platform.qt.QWidget`
        """

        super(TextFilterItemWidget, self).__init__(filter_id, group_id, parent=parent)

        self._name = filter_data.get("display_name", "")

        self.line_edit = search_widget.SearchWidget(self)
        self.line_edit.search_edited.connect(self.value_changed.emit)

        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    @FilterItemWidget.name.getter
    def name(self):
        """
        The display name for this widget.
        """

        return self._name

    @FilterItemWidget.value.getter
    def value(self):
        """
        Return the search widget's text value.
        """

        return self.line_edit.search_text

    @value.setter
    def value(self, value):
        """
        Set the search widget's text value.

        :param value: The text value to set.
        :type value: str
        """

        if not isinstance(value, six.string_types):
            assert False, "Attempt to set non-string data to QLineEdit"
            return

        self.line_edit.search_text = value
        self.value_changed.emit(value)

    def has_value(self):
        """
        Return True if the search widget has text, else False.
        """

        return bool(self.value)

    def clear_value(self):
        """
        Clear the search widget's text.
        """

        self.value = ""

    def restore(self, state):
        """
        Restore the search widget's text value.

        :param state: The state to restore the widget from.
        :type state: str | TextFilterItemWidget
        """

        if isinstance(state, TextFilterItemWidget):
            self.value = state.line_edit.search_text

        elif isinstance(state, six.string_types):
            self.value = state

        else:
            assert False, "Cannot restore TextFilterItemWidget state from '{}'".format(
                state
            )
