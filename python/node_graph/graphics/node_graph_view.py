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

# sg_qwidgets = sgtk.platform.current_bundle().import_module("sg_qwidgets")


class NodeGraphView(QtGui.QGraphicsView):
    """A widget to display a node graph."""

    # Emit signal to request the details widget to show/hide
    request_show_details = QtCore.Signal(bool)

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
        self.__node_graph.notifier.graph_node_added.connect(self.add_node)
        self.__node_graph.notifier.graph_node_removed.connect(self.remove_node)

        # The graphics items
        self.__root_node_item = None
        self.__node_items = {}
        self.__edge_items = []

        self.__view_mode = self.ViewMode.Default
        self.__timer_id = None

        self.setRenderHint(QtGui.QPainter.Antialiasing)

        scene = QtGui.QGraphicsScene(parent)
        self.setScene(scene)

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def root_node_item(self):
        """Get the super root node graphics item."""
        return self.__root_node_item

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

        self.__root_node_item = None
        self.__node_items = {}
        self.__edge_items = []
        self.scene().clear()

    def create_node_item(self, node):
        """Create and add a node graphics item to the view."""

        node_item = NodeItem(node, self, show_settings=self.show_node_settings())

        self.__node_items[node.id] = node_item
        self.scene().addItem(node_item)

        return node_item

    def create_edge_item(self, edge):
        """Add an edge graphics item to the graph."""

        input_node_item = self.node_items[edge.input_node.id]
        output_node_item = self.node_items[edge.output_node.id]

        edge_item = EdgeItem(input_node_item, output_node_item)
        self.__edge_items.append(edge_item)

        input_node_item.edge_items.append(edge_item)
        output_node_item.edge_items.append(edge_item)
        self.scene().addItem(edge_item)

        return edge_item

    def build(self):
        """
        Build the visual graph from the current node graph data.

        :param graph: The graph object containing the data to build the graph visually.
        :type graph. NodeGraph
        """

        # First clear the graph
        self.clear()

        # Create the super root node item
        root_node = self.__node_graph.root_node
        self.__root_node_item = self.create_node_item(root_node)

        # Create the rest of the nodes items
        for node in self.__node_graph.nodes.values():
            if node.id == self.__root_node_item.id:
                continue
            self.create_node_item(node)

        # Set the input/output node items for each node item (must be done after all node
        # items are created)
        for node in self.__node_graph.nodes.values():
            node_item = self.node_items[node.id]
            for output_node in node.outputs:
                output_node_item = self.node_items[output_node.id]
                node_item.output_node_items.append(output_node_item)
            for input_node in node.inputs:
                input_node_item = self.node_items[input_node.id]
                node_item.input_node_items.append(input_node_item)

        # Create the edge items connecting the node items
        for edge in self.__node_graph.edges:
            self.create_edge_item(edge)

        # Format the graph
        self.arrange_tree()

    def add_node(self, node):
        """Add a node to the current node graph view."""

        # First create the node item
        self.create_node_item(node)

        # Then, add the edges
        for edge in node.edges:
            self.create_edge_item(edge)

    def remove_node(self, node):
        """Remove the node from the node graph view."""

        node_item = self.node_items.get(node.id)
        if not node_item:
            return

        self.scene().removeItem(node_item)
        # TODO delete the node item - scene does not delete it

        for edge_item in node_item.edge_items:
            self.scene().removeItem(edge_item)
            # TODO remove the edge item from the other node
            # TODO delete the item - scene does not delete it

    def arrange_tree(self):
        """Arrange the node graph in a viewable format."""

        pos_x = 0
        pos_y = 0
        pos = QtCore.QPoint(pos_x, pos_y)
        self.__root_node_item.setPos(pos)

        # Then draw its children below in a tree-like structure
        hspace = 10
        vspace = 50
        nodes_to_arrange = [self.__root_node_item]
        while nodes_to_arrange:
            parent = nodes_to_arrange.pop()
            node_items = parent.output_node_items
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
                x_offset += node_item.boundingRect().width() + hspace
                nodes_to_arrange.append(node_item)

        for edge_item in self.edge_items:
            edge_item.adjust()

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
            node_item.show_settings = show_settings

        self.arrange_tree()

    # def build(self, graph):
    #     """
    #     Build the visual graph given the graph data.

    #     :param graph: The graph object containing the data to build the graph visually.
    #     :type graph. NodeGraph
    #     """

    #     # Clear the graph first
    #     self.clear()

    #     # Keep track of edges to add after all nodes have been created
    #     edges = []
    #     # Keep an edge graph to detect if an edge introduces a cycle
    #     edge_graph = {}
    #     # Keep track of child nodes to determine which nodes are top-level, which will need an
    #     # edge added to the root node
    #     child_nodes = set()
    #     # Keep track of node ids to prevent duplicates
    #     node_ids = set()

    #     # Create the nodes in the graph
    #     for data_id, data_value in data.items():
    #         if data_id == self.ROOT_NODE_ID:
    #             raise ValueError(
    #                 "Cannot use id for node '{}' - reservered for graph root node.".format(
    #                     data_id
    #                 )
    #             )

    #         if data_id in node_ids:
    #             raise ValueError(
    #                 "Cannot use id for node '{}' - not unique.".format(data_id)
    #             )

    #         node = NodeItem(data_id, data_value, self, show_settings=self.show_node_settings())
    #         self.add_node(data_id, node)

    #         output_node_ids = data_value.get("outputs", [])
    #         for output_node_id in output_node_ids:
    #             edges.append((data_id, output_node_id))
    #             edge_graph.setdefault(data_id, []).append(output_node_id)
    #             child_nodes.add(output_node_id)

    #     # Add edges to the nodes, while checking for cycles
    #     for edge_data in edges:
    #         input_id = edge_data[0]
    #         output_id = edge_data[1]

    #         # Ensure adding edge does not introduce a cycle in the graph. Detect cycle by
    #         # traversing the edge graph, if we can find our way back to the input node,
    #         # then there is a cycle. NOTE this approach is simple and could be optimized
    #         node_ids = edge_graph.get(output_id)
    #         while node_ids:
    #             node_id = node_ids.pop()
    #             if node_id == input_id:
    #                 raise self.NodeGraphCycleError("Detected cycle in node graph.")
    #             node_ids.extend(edge_graph.get(node_id, []))

    #         input_node = self.nodes.get(input_id)
    #         output_node = self.nodes.get(output_id)
    #         edge = input_node.add_output(output_node)
    #         self.add_edge(edge)

    #     # Add edges from top-level nodes to the root
    #     for node_id, node in self.nodes.items():
    #         if node_id == self.ROOT_NODE_ID:
    #             continue

    #         if node_id in child_nodes:
    #             continue

    #         edge = self.__root_node.add_output(node)
    #         self.add_edge(edge)

    # def item_moved(self):
    #     """
    #     Called when an item in the graph has changed position.

    #     This method's job is to simply start the restart the main timer in case it is not
    #     running already. the timer is designed to stop when the graph stabilizes, and start
    #     once it is unstable again.
    #     """

    #     # if not self.__timer_id:
    #     #     self.__timer_id = self.startTimer(1000 / 25)

    # def execute(self):
    #     """Traverse the graph starting from the root node and execute each node's function."""

    # nodes_to_process = deque()
    # nodes_to_process.append(self.__root_node)

    # # As nodes are executed, keep track of their results (to pass to their outputs)
    # node_results = {}

    # # No cycle detection required since this is checked at initial build time

    # while nodes_to_process:
    #     node = nodes_to_process.popleft()

    #     # Skip if the node has already been executed (if a node is an output of multiple
    #     # nodes, it will be added to the process list more than once)
    #     if node.id in node_results:
    #         continue

    #     # Ensure that all input nodes have executed before this node, and gather all input
    #     # node results to pass to this node
    #     inputs_ready = True
    #     input_data = {}
    #     for input_node in node.inputs:
    #         if not input_node.id in node_results:
    #             inputs_ready = False
    #             break

    #         node_data = node_results[input_node.id]
    #         # Merge the node data into the full input data
    #         # FIXME merge lists
    #         input_data.update(node_data)

    #     # Do not execute node if its inputs have not executed yet. Add it back to the list
    #     # of nodes to process once all inputs are ready
    #     if not inputs_ready:
    #         nodes_to_process.append(node)
    #         continue

    #     # Execute the node with all of its input data
    #     result = node.execute(input_data)
    #     # Store the result
    #     node_results[node.id] = result or {}
    #     # Add the node outputs to the list to process
    #     nodes_to_process.extend(node.outputs)

    # ----------------------------------------------------------------------------------------
    # Callbacks

    # ----------------------------------------------------------------------------------------
    # Override base QGraphicsView methods

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
