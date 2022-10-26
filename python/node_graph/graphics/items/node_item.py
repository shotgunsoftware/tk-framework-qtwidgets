# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from enum import Enum

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from tank_vendor import six

sg_qwidgets = sgtk.platform.current_bundle().import_module("sg_qwidgets")


class NodeItem(QtGui.QGraphicsItem):
    """The base node class."""

    def __init__(self, node, graph_view, show_settings=True, parent=None):
        """
        Initialize the node.

        :param parent: The parent of the node.
        :type parent: QGraphicsItem
        """

        super(NodeItem, self).__init__(parent)

        # QGraphicsItem properties
        self.setFlags(
            QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsSelectable
        )
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(-1)
        self.setAcceptHoverEvents(True)

        # Node properties
        self.__radius = node.data.get("radius", 6)
        self.__pen_width = node.data.get("pen_width", 2)
        self.__color = node.data.get("color", None)
        self.__highlight_color = node.data.get("color", None)
        self.__border_color = node.data.get("color", None)
        self.__text_padding = node.data.get("text_padding", 7)
        self.__text_margin = node.data.get("text_margin", 2)
        # This is specifically the header
        self.__text_alignment = node.data.get("text_alignment", QtCore.Qt.AlignCenter)

        self.__id = node.id
        self.__name = node.data.get("name", "Node")
        self.__description = node.data.get("description", "")
        # self.__exec_func = node.data.get("exec_func", None)
        # NOTE we may want to create a class to handle settings objects
        self.__settings = node.data.get("settings", {})

        self.__show_settings = show_settings

        self.__edge_items = []
        self.__input_node_items = []
        self.__output_node_items = []
        self.__graph = graph_view

        self.__node = node

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def id(self):
        """Return the unique id of the node."""
        return self.__id

    @property
    def name(self):
        """Get the name of the node."""
        return self.__name

    @property
    def description(self):
        """Get the description of the node."""
        return self.__description

    @property
    def radius(self):
        """Get the radius to draw the node."""
        return self.__radius

    @property
    def pen_width(self):
        """Get the pen width used to draw the node."""
        return self.__pen_width

    @property
    def edge_items(self):
        """Get the list of edge items that connect to this node."""
        return self.__edge_items

    @property
    def input_node_items(self):
        """Get the list of input node graphics items."""
        return self.__input_node_items

    @property
    def output_node_items(self):
        """Get the list of output node graphics items."""
        return self.__output_node_items

    @property
    def settings(self):
        """Get the current settings values."""
        return self.__settings

    @property
    def show_settings(self):
        """Get or set the property indicating if the settings are shown."""
        return self.__show_settings

    @show_settings.setter
    def show_settings(self, value):
        self.__show_settings = value

    # ----------------------------------------------------------------------------------------
    # Abstract methods

    # ----------------------------------------------------------------------------------------
    # Protected methods

    def _is_selected(self, option):
        """Return True if the node is currently selected."""

        return option.state & QtGui.QStyle.State_Selected

    def _is_hovered(self, option):
        """Return True if the mouse cursor is currently hovering over the node."""

        return option.state & QtGui.QStyle.State_MouseOver

    def _get_font_metrics(self):
        """Return the font metrics to use to render the node."""

        font = self.__graph.scene().font()
        return QtGui.QFontMetrics(font)

    def _get_header_bounding_rect(self, include_padding=True):
        """Return the bounding rect for the header text."""

        font_metrics = self._get_font_metrics()
        br = font_metrics.boundingRect(self.__name)

        if include_padding:
            # Add text padding to the rect
            br.setWidth(
                br.width()
                + 2 * self.__text_padding
                + 2 * self.__text_margin
                + 2 * self.pen_width
            )
            br.setHeight(
                br.height()
                + 2 * self.__text_padding
                + 2 * self.__text_margin
                + 2 * self.pen_width
            )

        return br

    def _get_settings_rect(self):
        """Return the bounding rect for the settings."""

        if not self.settings:
            return QtCore.QRectF()

        if not self.show_settings:
            return QtCore.QRectF()

        height = self.__text_padding
        width = 0
        font_metrics = self._get_font_metrics()

        for setting in self.settings.values():
            label_text = "{label}: ".format(label=setting["name"])
            label_rect = font_metrics.boundingRect(label_text)

            setting_type = setting["type"]
            value = setting.get("value", setting.get("default"))
            if setting_type is str:
                value_rect = font_metrics.boundingRect(value)
            elif setting_type is bool:
                value_rect = QtCore.QRectF(
                    0.0, 0.0, font_metrics.height(), font_metrics.height()
                )
            elif setting_type in (int, float):
                value_rect = font_metrics.boundingRect(str(value))
            elif setting_type is Enum:
                # TODO make this easier - we have to look up the display value here and in paint
                display_value = None
                choices = setting.get("choices", [])
                num_choices = len(choices)
                i = 0
                while display_value is None and i < num_choices:
                    if choices[i][1] == value:
                        display_value = choices[i][0]
                    i += 1
                value_rect = font_metrics.boundingRect(display_value)
            else:
                value_rect = QtCore.QRectF()

            height += (
                max(label_rect.height(), value_rect.height()) + self.__text_padding
            )
            width = max(
                width, label_rect.width() + self.__text_padding + value_rect.width()
            )

        width += 2 * self.__text_padding + 2 * self.__text_margin
        return QtCore.QRectF(0.0, 0.0, width, height)

    # ----------------------------------------------------------------------------------------
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """
        Override the base QGraphicsItem method.

        The node bounding rect will be calculated based on the text.
        """

        # TODO include options? or should those be displayed in a side details panel or popup?

        header_rect = self._get_header_bounding_rect()

        settings_rect = self._get_settings_rect()
        body_height = settings_rect.height()

        return QtCore.QRectF(
            0.0,
            0.0,
            max(header_rect.width(), settings_rect.width()),
            header_rect.height() + body_height,
        )

    def paint(self, painter, option, widget=None):
        """Override the base QGraphicsItem method"""

        # TODO include options? or should those be displayed in a side details panel or popup?

        rect = option.rect

        # Draw the background and border
        color = self.__color or option.palette.mid().color()
        border_color = self.__border_color or option.palette.light().color()
        brush = QtGui.QBrush(color)
        pen = QtGui.QPen(border_color, self.pen_width)
        painter.save()
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(rect, self.radius, self.radius)
        painter.restore()

        # Draw the text background
        header_rect = self._get_header_bounding_rect()
        text_rect = QtCore.QRectF(
            rect.x() + self.pen_width + self.__text_margin,
            rect.y() + self.pen_width + self.__text_margin,
            rect.width() - 2 * self.pen_width - 2 * self.__text_margin,
            header_rect.height() - 2 * self.pen_width - 2 * self.__text_margin,
        )
        painter.save()
        color = self.__color or option.palette.midlight().color()
        text_bg_brush = QtGui.QBrush(color)
        painter.setBrush(text_bg_brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(text_rect, self.radius - 2, self.radius - 2)
        painter.restore()

        # Draw the text
        painter.save()
        painter.drawText(text_rect, self.__text_alignment, self.name)
        painter.restore()

        #
        # Draw the settings
        #
        if self.show_settings:
            font_metrics = self._get_font_metrics()
            yoffset = text_rect.bottom() + self.__text_padding
            for setting in self.settings.values():
                label_text = "{label}: ".format(label=setting["name"])
                label_br = font_metrics.boundingRect(label_text)
                label_rect = QtCore.QRectF(
                    rect.x() + self.pen_width + self.__text_padding,
                    yoffset,
                    label_br.width(),
                    label_br.height(),
                )
                painter.save()
                painter.drawText(
                    label_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, label_text
                )
                painter.restore()

                setting_type = setting["type"]
                value = setting.get("value", setting.get("default"))

                if setting_type in (str, int, float):
                    if not isinstance(value, six.string_types):
                        value = str(value)

                    # TODO separate out to function
                    if value:
                        value_br = font_metrics.boundingRect(value)
                        value_rect = QtCore.QRectF(
                            label_rect.right() + self.__text_padding,
                            yoffset,
                            value_br.width(),
                            value_br.height(),
                        )
                        # Draw the value background
                        painter.save()
                        color = self.__color or option.palette.midlight().color()
                        text_bg_brush = QtGui.QBrush(color)
                        # TODO account for this added padding to the bounding rect
                        padding = 2
                        value_bg_rect = QtCore.QRectF(
                            value_rect.x() - padding,
                            value_rect.y() - padding,
                            value_rect.width() + padding * 2,
                            value_rect.height() + padding * 2,
                        )
                        painter.setBrush(text_bg_brush)
                        painter.setPen(QtCore.Qt.NoPen)
                        painter.drawRect(value_bg_rect)
                        painter.restore()
                        # Draw the value text
                        painter.save()
                        painter.drawText(
                            value_rect,
                            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft,
                            value,
                        )
                        painter.restore()
                elif setting_type is Enum:
                    # Need to get the display value for the current value
                    # NOTE should we index this so we don't have to search the list each time? would only matter if the list of choices is long
                    display_value = None
                    choices = setting.get("choices", [])
                    num_choices = len(choices)
                    i = 0
                    while display_value is None and i < num_choices:
                        if choices[i][1] == value:
                            display_value = choices[i][0]
                        i += 1

                    # TODO separate out to function (same as above)
                    if display_value:
                        value_br = font_metrics.boundingRect(display_value)
                        value_rect = QtCore.QRectF(
                            label_rect.right() + self.__text_padding,
                            yoffset,
                            value_br.width(),
                            value_br.height(),
                        )
                        # Draw the value background
                        painter.save()
                        color = self.__color or option.palette.midlight().color()
                        text_bg_brush = QtGui.QBrush(color)
                        # TODO account for this added padding to the bounding rect
                        padding = 2
                        value_bg_rect = QtCore.QRectF(
                            value_rect.x() - padding,
                            value_rect.y() - padding,
                            value_rect.width() + padding * 2,
                            value_rect.height() + padding * 2,
                        )
                        painter.setBrush(text_bg_brush)
                        painter.setPen(QtCore.Qt.NoPen)
                        painter.drawRect(value_bg_rect)
                        painter.restore()
                        # Draw the value text
                        painter.save()
                        painter.drawText(
                            value_rect,
                            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft,
                            display_value,
                        )
                        painter.restore()
                elif setting_type is bool:
                    # Draw a checkbox
                    button_option = QtGui.QStyleOptionButton()
                    button_option.rect = QtCore.QRect(
                        label_rect.right() + self.__text_padding,
                        yoffset,
                        font_metrics.height(),
                        font_metrics.height(),
                    )

                    button_option.state |= (
                        QtGui.QStyle.State_On if value else QtGui.QStyle.State_Off
                    )
                    style = widget.style() if widget else QtGui.QApplication.style()
                    style.proxy().drawControl(
                        QtGui.QStyle.CE_CheckBox, button_option, painter
                    )

                yoffset += font_metrics.height() + self.__text_padding

        #
        # Draw selection or hover
        #
        if self._is_selected(option) or self._is_hovered(option):
            painter.save()
            highlight_color = (
                self.__highlight_color or option.palette.highlight().color()
            )
            highlight_color.setAlpha(50)
            highlight_pen = QtGui.QPen(highlight_color, self.pen_width)
            painter.setBrush(highlight_color)
            painter.setPen(highlight_pen)
            painter.drawRoundedRect(rect, self.radius, self.radius)
            painter.restore()

        # #
        # # Draw 'executing' animation (blinking border?)
        # # FIXME need to do work in separate thread to update GUI while working
        # #
        # if self.__is_executing:
        #     painter.save()
        #     color = QtCore.Qt.yellow
        #     pen = QtGui.QPen(color, self.pen_width)
        #     painter.setBrush(color)
        #     painter.setPen(pen)
        #     painter.drawRoundedRect(rect, self.radius, self.radius)
        #     painter.restore()

        # Debugging...
        #
        settings_rect = self._get_settings_rect()
        painter.save()
        painter.setPen(QtCore.Qt.yellow)
        # painter.drawRect(text_rect)
        # painter.drawRect(rect)
        # painter.drawRect(settings_rect)
        painter.restore()

    def itemChange(self, change, value):
        """Override the base QGraphicsItem method."""

        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            for edge_item in self.edge_items:
                edge_item.adjust()

        return super(NodeItem, self).itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """Override the base QGraphicsItem method."""

        self.toggle_show_settings()

    def contextMenuEvent(self, event):
        """Override the base QGraphicsItem method."""

        actions = []

        edit_action = QtGui.QAction("Edit")
        edit_action.triggered.connect(lambda checked=False: self.__show_details())
        actions.append(edit_action)

        collapse_expand_action = QtGui.QAction(
            "Collpase" if self.show_settings else "Expand"
        )
        collapse_expand_action.triggered.connect(
            lambda checked=False: self.toggle_show_settings()
        )
        actions.append(collapse_expand_action)

        menu = sg_qwidgets.SGQMenu(self.__graph)
        menu.addActions(actions)
        menu.exec_(event.screenPos())

    # ----------------------------------------------------------------------------------------
    # Public methods

    def toggle_show_settings(self):
        """Toggle the property to show settings and update the view."""

        self.prepareGeometryChange()
        self.show_settings = not self.show_settings

        # Need to re-arrange the view now that this node has changed
        self.__graph.arrange_tree()

    # def add_edge(self, edge):
    #     """Add an edge to the node."""

    #     self.__edges.append(edge)
    #     edge.adjust()

    # def add_output(self, output_node):
    #     """Add an output node to this node and connect it with an edge."""

    #     edge = EdgeItem(self, output_node)
    #     self.add_edge(edge)

    #     self.__output_nodes.append(output_node)

    #     # Add input to this node to the output?
    #     output_node.add_input(self)
    #     # Add edge also to the output?
    #     output_node.add_edge(edge)

    #     return edge

    # def add_input(self, input_node):
    #     """Add an input node to this node andd connect it with an edge."""

    #     # edge = Edge(self, input_node)
    #     # self.add_edge(edge)

    #     self.__input_nodes.append(input_node)
    #     # return edge

    # def execute(self, input_data=None):
    #     """Execute the node's function, if it has one."""

    #     self.__is_executing = True

    #     try:
    #         print("Executing...", self.name)

    #         if not self.__exec_func:
    #             return

    #         return self.__exec_func(input_data, self.settings)
    #     finally:
    #         self.__is_executing = False

    # ----------------------------------------------------------------------------------------
    # Private methods

    def __show_details(self):
        """Request to show the details for this node."""

        # First clear the graph selection
        self.__graph.scene().clearSelection()
        # Ensure the details widget is showing
        self.__graph.request_show_details.emit(True)
        # Set the selection to this node only, which will display its details in the widget
        self.setSelected(True)
