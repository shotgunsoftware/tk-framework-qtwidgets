# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .edge import Edge

# NOTE
#   Different types of nodes
#   - input/read node (a node itself in the scene | file | stage for Alias | ...)
#   - output/write node (write to file)
#   - optimize/do something node (do optimization on input node)
#   - settings/options node (pass params to optimize node)


class Node(QtGui.QGraphicsItem):
    """The base node class."""

    def __init__(self, node_data, graph_widget, parent=None):
        """
        Initialize the node.

        :param parent: The parent of the node.
        :type parent: QGraphicsItem
        """

        super(Node, self).__init__(parent)

        # QGraphicsItem properties
        self.setFlags(
            QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsSelectable
        )
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(-1)
        self.setAcceptHoverEvents(True)

        # Node properties
        self.__radius = node_data.get("radius", 6)
        self.__pen_width = node_data.get("pen_width", 2)
        self.__color = node_data.get("color", None)
        self.__highlight_color = node_data.get("color", None)
        self.__border_color = node_data.get("color", None)
        self.__text_padding = node_data.get("text_padding", 7)
        self.__text_margin = node_data.get("text_margin", 2)
        # This is specifically the header
        self.__text_alignment = node_data.get("text_alignment", QtCore.Qt.AlignCenter)

        self.__name = node_data.get("name", "Node")
        self.__description = node_data.get("description", "")
        self.__exec_func = node_data.get("exec_func", None)
        self.__settings = node_data.get("settings", {})

        self.__edges = []
        self.__output_nodes = []
        self.__graph = graph_widget

        # Caller should do this?
        # self.__graph.add_node(self)

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def name(self):
        """Get the name of the node."""
        return self.__name

    @property
    def radius(self):
        """Get the radius to draw the node."""
        return self.__radius

    @property
    def pen_width(self):
        """Get the pen width used to draw the node."""
        return self.__pen_width

    @property
    def edges(self):
        """Get the list of the node's edges."""
        return self.__edges

    @property
    def outputs(self):
        """Get the list of output nodes."""
        return self.__output_nodes

    @property
    def settings(self):
        """Get the current settings values."""
        return self.__settings

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

        height = self.__text_padding
        width = 0
        font_metrics = self._get_font_metrics()

        for setting in self.settings.values():
            label_text = "{label}: ".format(label=setting["name"])
            label_rect = font_metrics.boundingRect(label_text)

            setting_type = setting["type"]
            if setting_type is str:
                value_rect = font_metrics.boundingRect(
                    setting.get("value", setting.get("default"))
                )
            elif setting_type is bool:
                value_rect = QtCore.QRectF(
                    0.0, 0.0, font_metrics.height(), font_metrics.height()
                )
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
            if setting_type is str:
                value_text = setting.get("value", setting.get("default"))
                if value_text:
                    value_br = font_metrics.boundingRect(value_text)
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
                        value_text,
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
                checked = setting.get("value", setting.get("default"))
                button_option.state |= (
                    QtGui.QStyle.State_On if checked else QtGui.QStyle.State_Off
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
            for edge in self.edges:
                edge.adjust()
            # self.__graph.itemMoved()

        return super(Node, self).itemChange(change, value)

    # ----------------------------------------------------------------------------------------
    # Public methods

    def add_edge(self, edge):
        """Add an edge to the node."""

        self.__edges.append(edge)
        edge.adjust()

    def add_output(self, output_node):
        """Add an output node to this node by connecting it with an edge."""

        edge = Edge(self, output_node)
        self.add_edge(edge)

        self.__output_nodes.append(output_node)
        return edge

    def execute(self, input_data=None):
        """Execute the node's function, if it has one."""

        print("Executing...", self.name)

        if not self.__exec_func:
            return

        return self.__exec_func(input_data, self.settings)
