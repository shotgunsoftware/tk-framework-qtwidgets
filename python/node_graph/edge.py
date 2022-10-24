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

    def __init__(self, source_node, dest_node, parent=None):
        """
        Initialize the edge.

        """

        super(Edge, self).__init__(parent)

        # QGraphicsItem properties
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        # Edge properties
        self.__source_node = source_node
        self.__dest_node = dest_node
        self.__source_point = None
        self.__dest_point = None
        self.__radius = 8
        self.__pen_width = 2

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

        connector_width = self.__radius
        connector_height = 2 * self.__radius
        extra_x = self.__pen_width + connector_width
        extra_y = self.__pen_width + connector_height

        return (
            QtCore.QRectF(
                self.source_point,
                QtCore.QSizeF(
                    self.dest_point.x() - self.source_point.x(),
                    self.dest_point.y() - self.source_point.y(),
                ),
            )
            .normalized()
            .adjusted(-extra_x, -extra_y, extra_x, extra_y)
        )

    def paint(self, painter, option, widget=None):
        """Override the base QGraphicsItem method"""

        # TODO use option and widget?
        # TODO make configurable?

        if not self.source_node or not self.dest_node:
            return

        # # Draw the line
        # line = QtCore.QLineF(self.source_point, self.dest_point)

        # if QtCore.qFuzzyCompare(line.length(), 0.0):
        #     return

        # Draw bezier curve connecting the source and destination points
        midpoint = QtCore.QPointF(
            (self.source_point.x() + self.dest_point.x()) / 2,
            (self.source_point.y() + self.dest_point.y()) / 2,
        )
        control_point1 = QtCore.QPointF(
            self.source_point.x(), midpoint.y() - (1 - 0.25) / 0.25
        )
        control_point2 = QtCore.QPointF(
            self.dest_point.x(), midpoint.y() - (1 - 0.75) / 0.75
        )
        path = QtGui.QPainterPath(self.source_point)
        path.cubicTo(control_point1, control_point2, self.dest_point)

        color = option.palette.mid().color()

        pen = QtGui.QPen(
            color,
            self.__pen_width,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.RoundJoin,
        )
        painter.setPen(pen)
        # painter.drawLine(line)
        painter.drawPath(path)

        # TODO separate out input/output to separate widget
        # TODO offset for multipl input/outputs so they don't overlap
        # Draw the input
        input_center = QtCore.QPointF(
            self.source_point.x(), self.source_point.y() - self.__radius
        )

        # Negative area between inner and outer
        color = option.palette.mid().color()
        brush = QtGui.QBrush(color)
        painter.save()
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(input_center, self.__radius, self.__radius)
        painter.restore()

        # Inner circle
        color = option.palette.light().color()
        # color = QtCore.Qt.darkYellow
        brush = QtGui.QBrush(color)
        painter.save()
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(input_center, self.__radius / 2, self.__radius / 2)
        painter.restore()

        # Outer circle
        color = option.palette.light().color()
        pen = QtGui.QPen(
            color,
            self.__pen_width,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.RoundJoin,
        )
        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawEllipse(input_center, self.__radius, self.__radius)
        painter.restore()

        # Draw the output
        output_center = QtCore.QPointF(
            self.dest_point.x(), self.dest_point.y() + self.__radius
        )

        # Negative area between inner and outer circles
        color = option.palette.light().color()
        brush = QtGui.QBrush(color)
        painter.save()
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(output_center, self.__radius, self.__radius)
        painter.restore()

        # Inner circle
        color = option.palette.mid().color()
        # color = QtCore.Qt.yellow
        brush = QtGui.QBrush(color)
        painter.save()
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(output_center, self.__radius / 2, self.__radius / 2)
        painter.restore()

        # Outer circle
        color = option.palette.mid().color()
        pen = QtGui.QPen(
            color,
            self.__pen_width,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.RoundJoin,
        )
        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawEllipse(output_center, self.__radius, self.__radius)
        painter.restore()

        # Debugging...
        #
        painter.save()
        painter.setPen(QtCore.Qt.yellow)
        # painter.drawRect(option.rect)
        painter.restore()

    # ----------------------------------------------------------------------------------------
    # Public methods

    def adjust(self):
        """Adjust the edge according to its source and destination nodes."""

        if not self.source_node or not self.dest_node:
            return

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
