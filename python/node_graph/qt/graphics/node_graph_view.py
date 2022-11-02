# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from enum import Enum, unique

from sgtk.platform.qt import QtCore, QtGui

from .items.node_item import NodeItem
from .items.edge_item import EdgeItem
from .items.connector_item import InputConnectorItem, OutputConnectorItem


class NodeGraphView(QtGui.QGraphicsView):
    """A widget to display a node graph."""

    # Emit signal to request the details widget to show/hide
    request_show_details = QtCore.Signal(bool)
    # Emit signal to request creating a new node
    request_add_node = QtCore.Signal(dict, QtCore.QPoint)
    # Emit signal to request creating a new edge between existing nodes
    request_add_edge = QtCore.Signal(str, str)

    @unique
    class ViewMode(Enum):
        """Enum class for view modes."""

        Default = 0
        Compact = 1

        @classmethod
        def is_valid(cls, value):
            """Return True if the given value is a valid ViewMode member."""

            # NOTE _value2member_map_ is undocumented and may change in future python
            return value in cls._value2member_map_

    def __init__(self, node_graph, parent=None):
        """
        Initialize the edge.

        :param parent: The parent of the graph widget.
        :type parent: QGraphicsItem
        """

        super(NodeGraphView, self).__init__(parent)

        # The node graph containing the graph data objects
        self.__node_graph = node_graph
        self.__node_graph.notifier.graph_end_reset.connect(self.build)
        # FIXME this is adding nodes during a graph build, only to be destroyed when reset
        self.__node_graph.notifier.graph_node_added.connect(self.add_node)
        self.__node_graph.notifier.graph_node_removed.connect(self.remove_node)
        self.__node_graph.notifier.graph_edge_added.connect(self.create_edge_item)
        # self.__node_graph.notifier.graph_edge_removed.connect(self.remove_edge)

        self.__view_mode = self.ViewMode.Default

        # The graphics items
        self.__root_node_items = []
        self.__node_items = {}
        self.__edge_items = []

        self.__pending_output_connector = None

        self.setRenderHints(
            QtGui.QPainter.Antialiasing
            | QtGui.QPainter.HighQualityAntialiasing
            | QtGui.QPainter.TextAntialiasing
            | QtGui.QPainter.SmoothPixmapTransform
        )
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)

        scene = QtGui.QGraphicsScene(parent)
        self.setScene(scene)

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def root_node_items(self):
        """Get the super root node graphics item."""
        return self.__root_node_items

    @property
    def node_items(self):
        """Get the mapping of node ids to graphics items."""
        return self.__node_items

    @property
    def edge_items(self):
        """Get the list of edge graphics items"""
        return self.__edge_items

    # ----------------------------------------------------------------------------------------
    # Public methods

    def show_node_settings(self):
        """Return True if the current view mode displays the node settings."""
        return self.__view_mode == self.ViewMode.Default

    def clear(self):
        """Clear the graph."""

        self.__root_node_items = []
        self.__node_items = {}
        self.__edge_items = []
        self.scene().clear()

    def create_node_item(self, node):
        """Create and add a node graphics item to the view."""

        node_item = NodeItem(node, self, show_settings=self.show_node_settings())

        self.__node_items[node.id] = node_item
        self.scene().addItem(node_item)

        return node_item

    def create_edge_item(self, input_node, output_node):
        """Add an edge graphics item to the graph."""

        input_node_item = self.node_items[input_node.id]
        output_node_item = self.node_items[output_node.id]

        input_node_connector = OutputConnectorItem(input_node_item)
        output_node_connector = InputConnectorItem(output_node_item)

        edge_item = EdgeItem(input_node_connector, output_node_connector)
        self.__edge_items.append(edge_item)

        input_node_item.edge_items.append(edge_item)
        output_node_item.edge_items.append(edge_item)

        self.scene().addItem(input_node_connector)
        self.scene().addItem(output_node_connector)
        self.scene().addItem(edge_item)

        return edge_item

    def start_output_connection(self, node_item):
        """Start an edge."""

        connector = OutputConnectorItem(node_item)
        # edge_item = EdgeItem(node_item)
        edge_item = EdgeItem(connector)

        self.scene().addItem(connector)
        self.scene().addItem(edge_item)

        return edge_item

    def end_output_connection(self, edge_item, output_node_item):
        """Complete the edge."""

        # # Create the output node connection and add it to the scene
        # output_node_connector = InputConnectorItem(output_node_item)
        # edge_item.destination_item = output_node_connector
        # self.scene().addItem(output_node_connector)

        # # Officially add the edge item to the node graph view
        # self.__edge_items.append(edge_item)

        # # Officially update node item edges
        # output_node_item.edge_items.append(edge_item)
        # edge_item.source_item.node_item.edge_items.append(edge_item)

        # Request the underlying node graph data structure to add the edge. The view will
        # receivev a signal if the edge is ok to add
        self.request_add_edge.emit(
            edge_item.source_item.node_item.id, output_node_item.id
        )

        # Remove the temporary connection from the view
        self.scene().removeItem(self.__pending_output_connector.source_item)

    def build(self):
        """
        Build the visual graph from the current node graph data.

        :param graph: The graph object containing the data to build the graph visually.
        :type graph. NodeGraph
        """

        # First clear the graph
        self.clear()

        # Create the rest of the nodes items
        for node in self.__node_graph.nodes.values():
            node_item = self.create_node_item(node)
            if not node.input_nodes:
                self.__root_node_items.append(node_item)

        # Create the edge items connecting the node items
        for edge in self.__node_graph.edges:
            self.create_edge_item(edge.input_node, edge.output_node)

        # Format the graph
        self.arrange_tree()

    def add_node(self, node):
        """
        Add a node to the current node graph view.

        NOTE: this should only be used once the graph has been built. It assumes all necessary
        nodes (for edges) have been created already.
        """

        # First create the node item
        self.create_node_item(node)

        # Then, add the edges
        for output_node in node.outputs:
            self.create_edge_item(node, output_node)
        for input_node in node.inputs:
            self.create_edge_item(input_node, node)

    def remove_node(self, node):
        """Remove the node from the node graph view."""

        node_item = self.node_items.get(node.id)
        if not node_item:
            return

        self.scene().removeItem(node_item)
        # TODO delete the node item - scene does not delete it

        # TODO node item will have edge items removed - look up from graph instead
        for edge_item in node_item.edge_items:
            self.scene().removeItem(edge_item)
            # TODO remove the edge item from the other node
            # TODO delete the item - scene does not delete it

    def arrange_tree(self):
        """Arrange the node graph in a viewable format."""

        pos_x = 0
        pos_y = 0
        pos = QtCore.QPoint(pos_x, pos_y)

        # Keep track of the nodes that have already been arranged (if nodes have more than one
        # input, they will be encountered multiple times to be arranged).
        arranged_node_ids = []

        for edge_item in self.edge_items:
            edge_item.prepareGeometryChange()

        for root_node_item in self.root_node_items:
            root_node_item.setPos(pos)
            arranged_node_ids.append(root_node_item.id)

            # Then draw its children below in a tree-like structure
            hspace = 10
            vspace = 50
            # nodes_to_arrange = [self.__root_node_item]
            nodes_to_arrange = [root_node_item]
            while nodes_to_arrange:
                parent = nodes_to_arrange.pop()

                node_items = [
                    self.node_items[node_id]
                    for node_id in parent.output_node_ids
                    if node_id not in arranged_node_ids
                ]

                y_offset = parent.pos().y() + parent.boundingRect().height() + vspace

                # First we need to calculate the level width to center the level of nows
                level_width = (
                    sum([node_item.boundingRect().width() for node_item in node_items])
                    + sum([hspace] * len(node_items))
                    - hspace
                )
                x_offset = (
                    parent.pos().x() + parent.boundingRect().width() / 2
                ) - level_width / 2

                for node_item in node_items:
                    pos = QtCore.QPoint(x_offset, y_offset)

                    node_item.setPos(pos)
                    arranged_node_ids.append(node_item.id)

                    x_offset += node_item.boundingRect().width() + hspace
                    nodes_to_arrange.append(node_item)

            # TODO for now we just offset the next subtree by a hard coded value - improve this.
            pos = QtCore.QPointF(pos_x + 200, pos_y)

        self.update()

    def set_view_mode(self, mode):
        """
        Set the graph view mode.

        :param mode: The view mode to set.
        :type mode:
        """

        if not isinstance(mode, self.ViewMode):
            raise Exception("Unsupported view mode '{}'".format(mode))

        if mode == self.__view_mode:
            return

        self.__view_mode = mode
        show_settings = self.__view_mode == self.ViewMode.Default

        for node_item in self.node_items.values():
            node_item.prepareGeometryChange()
            node_item.show_settings = show_settings

        self.arrange_tree()

    # ----------------------------------------------------------------------------------------
    # Callbacks

    # ----------------------------------------------------------------------------------------
    # Override base QGraphicsView methods

    def dragEnterEvent(self, event):
        print("view drag enter")
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        print("view drag move")
        event.acceptProposedAction()

    def dropEvent(self, event):
        """ """

        source_widget = event.source()
        print("view drop event", source_widget)

        if isinstance(source_widget, QtGui.QListWidget):
            item = source_widget.currentItem()
            print(item, item.text())

            node_data = item.data(QtCore.Qt.UserRole)

            # Request a node to be added to the underlying data structure for the graph view,
            # which will eventually callback the graph view's create node item function to tadd
            # it to the UI
            self.request_add_node.emit(node_data, event.pos())

    def mousePressEvent(self, event):
        """Override the base QGraphicsItem method."""

        if event.button() == QtCore.Qt.LeftButton:
            item = self.itemAt(event.pos())

            if isinstance(item, NodeItem):
                scene_pos = self.mapToScene(event.pos())
                target_rect = item.sceneBoundingRect()
                target_rect.setY(target_rect.y() + target_rect.height() * 0.85)

                if target_rect.contains(scene_pos):
                    # NOTE for now just any click on the bottom of the node will start an output connection

                    self.__pending_output_connector = self.start_output_connection(item)
                    return

                # elif event.pos().y() < self.boundingRect().top() + self.boundingRect().height()*0.15:
                #     # NOTE for now just any click on the top of the node will start an input connection

                #     self.start_input_connection()

        super(NodeGraphView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Override the base QGraphicsItem method."""

        if self.__pending_output_connector:
            scene_pos = self.mapToScene(event.pos())
            item_pos = self.__pending_output_connector.mapFromScene(scene_pos)
            self.__pending_output_connector.destination_point = item_pos
            return

        super(NodeGraphView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Override the base QGraphicsItem method."""

        if event.button() == QtCore.Qt.LeftButton:
            if self.__pending_output_connector:
                item = self.itemAt(event.pos())

                if (
                    isinstance(item, NodeItem)
                    and item.id
                    != self.__pending_output_connector.source_item.node_item.id
                ):
                    # Finish creating the output connection
                    # self.__pending_output_connector.destination_item = item
                    self.end_output_connection(self.__pending_output_connector, item)

                    # self.scene().removeItem(self.__pending_output_connector)
                    self.__pending_output_connector = None
                    return
                else:
                    # Remove the pending connection
                    self.scene().removeItem(self.__pending_output_connector.source_item)
                    # self.scene().removeItem(self.__pending_output_connector)
                    self.__pending_output_connector = None
                    return

        super(NodeGraphView, self).mouseReleaseEvent(event)

    # def timerEvent(self, eevent):
    #     """The timer event callback method"""

    #     nodes = []
    #     for item in self.scene().items():
    #         if isinstance(item, Node):
    #             nodes.append(item)

    # def contextMenuEvent(self, event):
    #     """Override the base class method."""

    #     # TODO contxt menu event on the scene

    #     item = self.itemAt(event.pos())
    #     if item:
    #         pos = self.mapToScene(event.pos())
    #         item.show_context_menu(pos)
    #     else:
    #         print("Graphics View Context Menu")
    #         event.accept()
