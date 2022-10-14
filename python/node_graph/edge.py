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


class Edge(QtGui.QGraphicsItem):
    """A class to represent an edge connecting two nodes in a graph."""

    def __init__(self, source_node, dest_node):
        """
        Initialize the edge.

        """

        super(Edge, self).__init__()

        # QGraphicsItem properties
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        # Edge properties
        self.__source_node = source_node
        self.__dest_node = dest_node
        self.__source_point = None
        self.__dest_point = None
        self.__arrow_size = 10

        # Initialize the edge
        self.source_node.add_edge(self)
        self.dest_node.add_edge(self)
        self.adjust()

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def source_node(self):
        """Get or set the source ndoe of this edge (the start point)."""
        return self.__source_node

    @source_node.setter
    def source_node(self, node):
        self.__source_node = node

    @property
    def dest_node(self):
        """Get or set the destination ndoe of this edge (the end point)."""
        return self.__dest_node

    @dest_node.setter
    def dest_node(self, node):
        self.__dest_node = node

    @property
    def source_point(self):
        """Get the source point for the edge."""
        return self.__source_point

    @property
    def dest_point(self):
        """Get the destination point for the edge."""
        return self.__dest_point

    # ----------------------------------------------------------------------------------------
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """Override the base QGraphicsItem method"""

        if not self.source_node or not self.dest_node:
            return QtCore.QRectF()

        # TODO make configurable
        pen_width = 1
        extra = (pen_width + self.__arrow_size) / 2.0

        return (
            QtCore.QRectF(
                self.source_point,
                QtCore.QSizeF(
                    self.dest_point.x() - self.source_point.x(),
                    self.dest_point.y() - self.source_point.y(),
                ),
            )
            .normalized()
            .adjusted(-extra, -extra, extra, extra)
        )

    def paint(self, painter, option, widget=None):
        """Override the base QGraphicsItem method"""

        # TODO use option and widget?
        # TODO make configurable?

        if not self.source_node or not self.dest_node:
            return

        # Draw the line
        line = QtCore.QLineF(self.source_point, self.dest_point)
        if QtCore.qFuzzyCompare(line.length(), 0.0):
            return

        color = option.palette.mid().color()
        pen_width = 2

        pen = QtGui.QPen(
            color,
            pen_width,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.RoundJoin,
        )
        painter.setPen(pen)
        painter.drawLine(line)

        # TODO draw the arrows or input/output circles

    # ----------------------------------------------------------------------------------------
    # Public methods

    def adjust(self):
        """Adjust the edge according to its source and destination nodes."""

        if not self.source_node or not self.dest_node:
            return

        # FIXME start / end the line not from the top right of the objects
        # line = QtCore.QLineF(
        #     self.mapFromItem(self.source_node, 0, 0),
        #     self.mapFromItem(self.dest_node, 0, 0),
        # )
        line = QtCore.QLineF(
            self.mapFromItem(
                self.source_node,
                self.source_node.sceneBoundingRect().width() / 2,
                self.source_node.sceneBoundingRect().height(),
            ),
            self.mapFromItem(
                self.dest_node, self.dest_node.sceneBoundingRect().width() / 2, 0
            ),
        )
        length = line.length()

        self.prepareGeometryChange()

        if length > 20.0:
            edge_offset = QtCore.QPointF(
                (line.dx() * 10) / length, (line.dy() * 10) / length
            )
            self.__source_point = line.p1() + edge_offset
            self.__dest_point = line.p2() - edge_offset
        else:
            self.__source_point = line.p1()
            self.__dest_point = line.p1()
