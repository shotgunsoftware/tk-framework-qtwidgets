# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from email import header
import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .edge import Edge


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
        self.__width = node_data.get("width", 150)
        self.__height = node_data.get("height", 50)
        self.__pos = node_data.get("pos", QtCore.QPointF(0, 0))
        self.__pen_width = node_data.get("pen_width", 2)
        self.__color = node_data.get("color", None)
        self.__highlight_color = node_data.get("color", None)
        self.__border_color = node_data.get("color", None)
        self.__text_padding = node_data.get("text_padding", 7)
        self.__text_margin = node_data.get("text_padding", 2)
        self.__text_alignment = node_data.get("text_alignment", QtCore.Qt.AlignCenter)

        self.__name = node_data.get("name", "Node")
        self.__description = node_data.get("description", "")
        self.__exec_func = node_data.get("exec_func", None)

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
    def pos(self):
        """Get the position to draw the node."""
        return self.__pos

    @property
    def radius(self):
        """Get the radius to draw the node."""
        return self.__radius

    @property
    def width(self):
        """Get the width of the node."""
        return self.__width

    @property
    def height(self):
        """Get the height of the node."""
        return self.__height

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

    # ----------------------------------------------------------------------------------------
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """
        Override the base QGraphicsItem method.

        The node bounding rect will be calculated based on the text.
        """

        body_height = 40
        header_rect = self._get_header_bounding_rect()

        return QtCore.QRectF(
            self.pos.x(),
            self.pos.y(),
            header_rect.width(),
            header_rect.height() + body_height,
        )

    def paint(self, painter, option, widget=None):
        """Override the base QGraphicsItem method"""

        # TODO draw selection
        # TODO draw hover

        # Draw the background and border
        color = self.__color or option.palette.mid().color()
        border_color = self.__border_color or option.palette.light().color()
        brush = QtGui.QBrush(color)
        pen = QtGui.QPen(border_color, self.pen_width)
        painter.save()
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(option.rect, self.radius, self.radius)
        painter.restore()

        # Draw the text background
        header_rect = self._get_header_bounding_rect()
        text_rect = QtCore.QRectF(
            option.rect.x() + self.pen_width + self.__text_margin,
            option.rect.y() + self.pen_width + self.__text_margin,
            header_rect.width() - 2 * self.pen_width - 2 * self.__text_margin,
            header_rect.height() - 2 * self.pen_width - 2 * self.__text_margin,
        )
        painter.save()
        color = self.__color or option.palette.midlight().color()
        text_bg_brush = QtGui.QBrush(color)
        painter.setBrush(text_bg_brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(text_rect, self.radius, self.radius)
        painter.restore()

        # Draw the text background
        painter.save()
        painter.drawText(text_rect, self.__text_alignment, self.name)
        painter.restore()

        # Draw selection or hover
        if self._is_selected(option) or self._is_hovered(option):
            painter.save()
            highlight_color = (
                self.__highlight_color or option.palette.highlight().color()
            )
            highlight_color.setAlpha(50)
            highlight_pen = QtGui.QPen(highlight_color, self.pen_width)
            painter.setBrush(highlight_color)
            painter.setPen(highlight_pen)
            painter.drawRoundedRect(option.rect, self.radius, self.radius)
            painter.restore()

        # Debugging...
        #
        painter.save()
        painter.setPen(QtCore.Qt.yellow)
        # painter.drawRect(text_rect)
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

        # TODO gather settings?
        # TODO define what input_data is
        return self.__exec_func(input_data)
