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
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(-1)

        # Node properties
        self.__radius = node_data.get("radius", 6)
        self.__width = node_data.get("width", 200)
        self.__height = node_data.get("height", 150)
        self.__pen_width = node_data.get("pen_width", 2)
        self.__pos = node_data.get("pos", QtCore.QPointF(0, 0))

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
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """Override the base QGraphicsItem method"""

        return QtCore.QRectF(self.pos.x(), self.pos.y(), self.width, self.height)

    def paint(self, painter, option, widget=None):
        """Override the base QGraphicsItem method"""

        # TODO use option and widget?
        # TODO make this configurable

        # Draw the shape
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.darkGray)
        painter.drawRoundedRect(option.rect, self.radius, self.radius)

        # Draw the text
        painter.drawText(option.rect, self.name)

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
