# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import math

from sgtk.platform.qt import QtCore, QtGui


class EdgeItem(QtGui.QGraphicsPathItem):
    """A class to represent an edge connecting two nodes in a graph."""

    EDGE_CP_ROUNDNESS = 100  #: Bezier control point distance on the line

    def __init__(self, input_connector, output_connector=None):
        """Initialize the edge."""

        super(EdgeItem, self).__init__(input_connector)
        # super(EdgeItem, self).__init__(parent=None)

        # QGraphicsItem properties
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        # self.setFlags(
        #     QtGui.QGraphicsItem.ItemIsMovable
        # )
        self.setZValue(-1)

        # Edge properties
        self.__src_item = input_connector
        self.__dest_item = output_connector
        self.__dst_point = None

        self.__pen_width = 2

        # Initialize the edge
        # self.adjust()

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def source_item(self):
        """Get the source graphics item that this edge item starts at."""
        return self.__src_item

    @property
    def destination_item(self):
        """Get or set the destination graphics item that this edge item ends at."""
        return self.__dest_item

    @destination_item.setter
    def destination_item(self, value):
        self.prepareGeometryChange()
        self.__dest_item = value

    @property
    def destination_point(self):
        """Get or set the destination point. This property is ignored if the destination_item property is not None."""
        return self.__dst_point

    @destination_point.setter
    def destination_point(self, value):
        self.prepareGeometryChange()
        self.__dst_point = value

    # ----------------------------------------------------------------------------------------
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """Override the base QGraphicsItem method"""

        return self.shape().boundingRect()

    def shape(self):
        """Return the shape of the edge's path."""

        return self.calc_path()

    def calc_path(self):
        """Calculate the Bezier path"""

        s = self.get_start_point()
        d = self.get_end_point()

        if not s or not d:
            return QtGui.QPainterPath()

        # #
        # # Draw bezier curve method #1
        # #
        # dist = (d.x() - s.x()) * 0.5
        # cpx_s = +dist
        # cpx_d = -dist
        # cpy_s = 0
        # cpy_d = 0
        # if s.x() > d.x():
        #     cpx_d *= -1
        #     cpx_s *= -1
        #     cpy_d = ((s.y() - d.y()) / math.fabs((s.y() - d.y()) if (s.y() - d.y()) != 0 else 0.00001)) * self.EDGE_CP_ROUNDNESS
        #     cpy_s = ((d.y() - s.y()) / math.fabs((d.y() - s.y()) if (d.y() - s.y()) != 0 else 0.00001)) * self.EDGE_CP_ROUNDNESS
        # path = QtGui.QPainterPath(QtCore.QPointF(s.x(), s.y()))
        # path.cubicTo(s.x() + cpx_s, s.y() + cpy_s, d.x() + cpx_d, d.y() + cpy_d, d.x(), d.y())

        #
        # Draw bezier curve method #2
        #
        midpoint = QtCore.QPointF(
            (s.x() + d.x()) / 2,
            (s.y() + d.y()) / 2,
        )
        control_point1 = QtCore.QPointF(s.x(), midpoint.y() - (1 - 0.25) / 0.25)
        control_point2 = QtCore.QPointF(d.x(), midpoint.y() - (1 - 0.75) / 0.75)
        path = QtGui.QPainterPath(s)
        path.cubicTo(control_point1, control_point2, d)

        return path

    def paint(self, painter, option, widget=None):
        """Override the base QGraphicsItem method"""

        color = option.palette.mid().color()
        pen = QtGui.QPen(
            color,
            self.__pen_width,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.RoundJoin,
        )

        self.setPath(self.shape())

        # painter.setPen(pen if not self.isSelected() else self.__pen_selected)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(self.path())

        # Debugging...
        #
        painter.save()
        painter.setPen(QtCore.Qt.yellow)
        # painter.drawRect(option.rect)
        # painter.setPen(QtCore.Qt.cyan)
        # painter.drawRect(self.source_item.boundingRect())
        # painter.setPen(QtCore.Qt.magenta)
        # painter.drawRect(self.destination_item.boundingRect())
        painter.restore()

    def get_start_point(self):
        """Return the start point for this edge item."""

        # return self.mapFromItem(
        #     self.source_item,
        #     self.source_item.sceneBoundingRect().width() / 2,
        #     self.source_item.sceneBoundingRect().height(),
        # )
        return self.mapFromItem(
            self.source_item,
            self.source_item.boundingRect().left()
            + self.source_item.boundingRect().width() / 2,
            self.source_item.boundingRect().top()
            + self.source_item.boundingRect().height() / 2,
        )

    def get_end_point(self):
        """Return the end point for this edge item."""

        if self.destination_item:
            # return self.mapFromItem(
            #     self.destination_item,
            #     self.destination_item.sceneBoundingRect().width() / 2,
            #     0
            # )
            return self.mapFromItem(
                self.destination_item,
                self.destination_item.boundingRect().left()
                + self.destination_item.boundingRect().width() / 2,
                self.destination_item.boundingRect().top()
                + self.destination_item.boundingRect().height() / 2,
            )
        else:
            return self.destination_point


# # Copyright (c) 2022 Autodesk, Inc.
# #
# # CONFIDENTIAL AND PROPRIETARY
# #
# # This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# # Source Code License included in this distribution package. See LICENSE.
# # By accessing, using, copying or modifying this work you indicate your
# # agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# # not expressly granted therein are reserved by Autodesk, Inc.

# from sgtk.platform.qt import QtCore, QtGui

# class EdgeItem(QtGui.QGraphicsItem):
#     """A class to represent an edge connecting two nodes in a graph."""

#     def __init__(self, input_node_item, output_node_item, parent=None):
#         """Initialize the edge."""

#         super(EdgeItem, self).__init__(parent)

#         # QGraphicsItem properties
#         # TODO allow edges to move to edit input/output
#         # NOTE we may want to separate out edge and "connector" to different classes to chagne input/outputs
#         self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
#         # self.setFlags(
#         #     QtGui.QGraphicsItem.ItemIsMovable
#         # )

#         # Edge properties
#         self.__source_node = input_node_item
#         self.__dest_node = output_node_item
#         self.__source_point = None
#         self.__dest_point = None
#         self.__radius = 8
#         self.__pen_width = 2

#         # # Initialize the edge
#         self.adjust()

#     # ----------------------------------------------------------------------------------------
#     # Properties

#     @property
#     def source_node(self):
#         """Get or set the source ndoe of this edge (the start point)."""
#         return self.__source_node

#     @source_node.setter
#     def source_node(self, node):
#         self.__source_node = node

#     @property
#     def dest_node(self):
#         """Get or set the destination ndoe of this edge (the end point)."""
#         return self.__dest_node

#     @dest_node.setter
#     def dest_node(self, node):
#         self.__dest_node = node

#     @property
#     def source_point(self):
#         """Get the source point for the edge."""
#         return self.__source_point

#     @property
#     def dest_point(self):
#         """Get the destination point for the edge."""
#         return self.__dest_point

#     # ----------------------------------------------------------------------------------------
#     # QGraphicsItem pure virtual methods

#     def boundingRect(self):
#         """Override the base QGraphicsItem method"""

#         if not self.source_node or not self.dest_node:
#             return QtCore.QRectF()

#         extra_x = self.__pen_width
#         extra_y = self.__pen_width

#         return (
#             QtCore.QRectF(
#                 self.source_point,
#                 QtCore.QSizeF(
#                     self.dest_point.x() - self.source_point.x(),
#                     self.dest_point.y() - self.source_point.y(),
#                 ),
#             )
#             .normalized()
#             .adjusted(-extra_x, -extra_y, extra_x, extra_y)
#         )

#     def paint(self, painter, option, widget=None):
#         """Override the base QGraphicsItem method"""

#         if not self.source_node or not self.dest_node:
#             return

#         # Draw bezier curve connecting the source and destination points
#         midpoint = QtCore.QPointF(
#             (self.source_point.x() + self.dest_point.x()) / 2,
#             (self.source_point.y() + self.dest_point.y()) / 2,
#         )
#         control_point1 = QtCore.QPointF(
#             self.source_point.x(), midpoint.y() - (1 - 0.25) / 0.25
#         )
#         control_point2 = QtCore.QPointF(
#             self.dest_point.x(), midpoint.y() - (1 - 0.75) / 0.75
#         )
#         path = QtGui.QPainterPath(self.source_point)
#         path.cubicTo(control_point1, control_point2, self.dest_point)

#         color = option.palette.mid().color()

#         pen = QtGui.QPen(
#             color,
#             self.__pen_width,
#             QtCore.Qt.SolidLine,
#             QtCore.Qt.RoundCap,
#             QtCore.Qt.RoundJoin,
#         )
#         painter.setPen(pen)
#         # painter.drawLine(line)
#         painter.drawPath(path)

#         # Debugging...
#         #
#         painter.save()
#         painter.setPen(QtCore.Qt.yellow)
#         # painter.drawRect(option.rect)
#         painter.restore()

#     # ----------------------------------------------------------------------------------------
#     # Public methods

#     def adjust(self):
#         """Adjust the edge according to its source and destination nodes."""

#         if not self.source_node or not self.dest_node:
#             return

#         line = QtCore.QLineF(
#             self.mapFromItem(
#                 self.source_node,
#                 self.source_node.sceneBoundingRect().width() / 2,
#                 self.source_node.sceneBoundingRect().height(),
#             ),
#             self.mapFromItem(
#                 self.dest_node, self.dest_node.sceneBoundingRect().width() / 2, 0
#             ),
#         )
#         length = line.length()

#         self.prepareGeometryChange()

#         if length > 20.0:
#             edge_offset = QtCore.QPointF(
#                 (line.dx() * 10) / length, (line.dy() * 10) / length
#             )
#             self.__source_point = line.p1() + edge_offset
#             self.__dest_point = line.p2() - edge_offset
#         else:
#             self.__source_point = line.p1()
#             self.__dest_point = line.p1()
