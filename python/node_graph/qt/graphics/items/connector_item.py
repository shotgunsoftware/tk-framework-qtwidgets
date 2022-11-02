# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from sgtk.platform.qt import QtCore, QtGui


class ConnectorItem(QtGui.QGraphicsItem):
    """A class to represent a node input or output connector."""

    def __init__(self, node_item):
        """Initialize the connector."""

        super(ConnectorItem, self).__init__(node_item)

        # The node this connector is for
        self.__node_item = node_item

        self.__radius = 8
        self.__pen_width = 2

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def node_item(self):
        """Get the node item that this conentor belongs to."""
        return self.__node_item

    @property
    def radius(self):
        """Get the radius for the connector item."""
        return self.__radius

    @property
    def pen_width(self):
        """Get the pen width for the connector item."""
        return self.__pen_width

    # ----------------------------------------------------------------------------------------
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """Override the base QGraphicsItem method"""

        raise NotImplementedError("Subclass must implement this method")

    def paint(self, painter, option, widget=None):
        """Override the base QGraphicsItem method"""

        # TODO allow horizontal position (e.g. flow left to right instead of top to bottom)

        rect = option.rect
        center = QtCore.QPointF(
            rect.left() + rect.width() / 2,
            rect.top() + rect.height() / 2,
        )

        # Negative area between inner and outer circles
        color = option.palette.light().color()
        brush = QtGui.QBrush(color)
        painter.save()
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(center, self.radius, self.radius)
        painter.restore()

        # Inner circle
        color = option.palette.mid().color()
        brush = QtGui.QBrush(color)
        painter.save()
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(center, self.radius / 2, self.radius / 2)
        painter.restore()

        # Outer circle
        color = option.palette.mid().color()
        pen = QtGui.QPen(
            color,
            self.pen_width,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.RoundJoin,
        )
        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawEllipse(center, self.radius, self.radius)
        painter.restore()

        # Debugging...
        #
        painter.save()
        painter.setPen(QtCore.Qt.cyan)
        # painter.drawRect(option.rect)
        painter.restore()


class InputConnectorItem(ConnectorItem):
    """A class to represent a node input or output connector."""

    def __init__(self, node_item):
        """Initialize the connector."""

        super(InputConnectorItem, self).__init__(node_item)

    # ----------------------------------------------------------------------------------------
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """Override the base QGraphicsItem method"""

        if not self.node_item:
            return QtCore.QRectF()

        node_br = self.node_item.boundingRect()

        # TODO determine where to draw the connector on the node better
        pos = QtCore.QPointF(
            node_br.left() + node_br.width() / 2 - self.radius,
            node_br.top() - self.radius,
        )

        extra_x = self.pen_width
        extra_y = self.pen_width

        return (
            QtCore.QRectF(pos, QtCore.QSizeF(2 * self.radius, 2 * self.radius))
            .normalized()
            .adjusted(-extra_x, -extra_y, extra_x, extra_y)
        )


class OutputConnectorItem(ConnectorItem):
    """A class to represent a node output connector."""

    def __init__(self, node_item):
        """Initialize the connector."""

        super(OutputConnectorItem, self).__init__(node_item)

    # ----------------------------------------------------------------------------------------
    # QGraphicsItem pure virtual methods

    def boundingRect(self):
        """Override the base QGraphicsItem method"""

        if not self.node_item:
            return QtCore.QRectF()

        node_br = self.node_item.boundingRect()

        # TODO determine where to draw the connector on the node better
        pos = QtCore.QPointF(
            node_br.left() + node_br.width() / 2 - self.radius,
            node_br.bottom() - self.radius,
        )

        extra_x = self.pen_width
        extra_y = self.pen_width

        return (
            QtCore.QRectF(pos, QtCore.QSizeF(2 * self.radius, 2 * self.radius))
            .normalized()
            .adjusted(-extra_x, -extra_y, extra_x, extra_y)
        )
