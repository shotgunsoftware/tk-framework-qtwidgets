# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from collections import deque

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .node import Node
from .edge import Edge


class GraphWidget(QtGui.QGraphicsView):
    """A widget to display a node graph."""

    class NodeGraphCycleError(Exception):
        """Custom exception class to throw when a cycle in the graph is detected."""

    # TODO ensure no nodes use this id when creating nodes
    ROOT_NODE_ID = "__root__"

    def __init__(self, parent=None):
        """
        Initialize the edge.

        :param parent: The parent of the graph widget.
        :type parent: QGraphicsItem
        """

        super(GraphWidget, self).__init__(parent)

        self.__nodes = {}
        self.__edges = {}
        self.__timer_id = None

        scene = QtGui.QGraphicsScene(parent)
        self.setScene(scene)

        self.setRenderHint(QtGui.QPainter.Antialiasing)

        self.__root_node = Node(self.ROOT_NODE_ID, {"name": "Start"}, self)
        self.add_node(self.__root_node.id, self.__root_node)

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def nodes(self):
        """Get the list of nodes in the graph."""
        return self.__nodes

    # ----------------------------------------------------------------------------------------
    # Override base QGraphicsView methods

    # def timerEvent(self, eevent):
    #     """The timer event callback method"""

    #     nodes = []
    #     for item in self.scene().items():
    #         if isinstance(item, Node):
    #             nodes.append(item)

    # ----------------------------------------------------------------------------------------
    # Public methods

    def clear(self):
        """Clear the graph."""

        # NOTE do we need to delete nodes?
        self.__nodes = {}
        self.__edges = []

        self.scene().clear()

        # TODO handle this better
        self.__root_node = Node(self.ROOT_NODE_ID, {"name": "Start"}, self)
        self.add_node(self.__root_node.id, self.__root_node)

    def add_node(self, node_id, node):
        """
        Add a node to the graph.

        :param node: THe node to add to the graph.
        :type node: Node
        """

        self.__nodes[node_id] = node
        self.scene().addItem(node)

    def add_edge(self, edge):
        """Add an edge to the graph."""

        self.scene().addItem(edge)
        self.__edges.append(edge)

    def build(self, data):
        """Build the graph given the data."""

        # Clear the graph first
        self.clear()

        # Keep track of edges to add after all nodes have been created
        edges = []
        # Keep an edge graph to detect if an edge introduces a cycle
        edge_graph = {}
        # Keep track of child nodes to determine which nodes are top-level, which will need an
        # edge added to the root node
        child_nodes = set()
        # Keep track of node ids to prevent duplicates
        node_ids = set()

        # Create the nodes in the graph
        for data_id, data_value in data.items():
            if data_id == self.ROOT_NODE_ID:
                raise ValueError(
                    "Cannot use id for node '{}' - reservered for graph root node.".format(
                        data_id
                    )
                )

            if data_id in node_ids:
                raise ValueError(
                    "Cannot use id for node '{}' - not unique.".format(data_id)
                )

            node = Node(data_id, data_value, self)
            self.add_node(data_id, node)

            output_node_ids = data_value.get("outputs", [])
            for output_node_id in output_node_ids:
                edges.append((data_id, output_node_id))
                edge_graph.setdefault(data_id, []).append(output_node_id)
                child_nodes.add(output_node_id)

        # Add edges to the nodes, while checking for cycles
        for edge_data in edges:
            input_id = edge_data[0]
            output_id = edge_data[1]

            # Ensure adding edge does not introduce a cycle in the graph. Detect cycle by
            # traversing the edge graph, if we can find our way back to the input node,
            # then there is a cycle. NOTE this approach is simple and could be optimized
            node_ids = edge_graph.get(output_id)
            while node_ids:
                node_id = node_ids.pop()
                if node_id == input_id:
                    raise self.NodeGraphCycleError("Detected cycle in node graph.")
                node_ids.extend(edge_graph.get(node_id, []))

            input_node = self.nodes.get(input_id)
            output_node = self.nodes.get(output_id)
            edge = input_node.add_output(output_node)
            self.add_edge(edge)

        # Add edges from top-level nodes to the root
        for node_id, node in self.nodes.items():
            if node_id == self.ROOT_NODE_ID:
                continue

            if node_id in child_nodes:
                continue

            edge = self.__root_node.add_output(node)
            self.add_edge(edge)

    def arrange_tree(self):
        """Arrange the node graph in a viewable format."""

        pos_x = 0
        pos_y = 0
        pos = QtCore.QPoint(pos_x, pos_y)
        self.__root_node.setPos(pos)

        # Then draw its children below in a tree-like structure
        hspace = 10
        vspace = 50
        nodes_to_arrange = [self.__root_node]
        while nodes_to_arrange:
            parent = nodes_to_arrange.pop()
            nodes = parent.outputs
            y_offset = parent.pos().y() + parent.boundingRect().height() + vspace

            # First we need to calculate the level width to center the level of nows
            level_width = (
                sum([node.boundingRect().width() for node in nodes])
                + sum([hspace] * len(nodes))
                - hspace
            )
            x_offset = (
                parent.pos().x() + parent.boundingRect().width() / 2
            ) - level_width / 2

            for node in nodes:
                pos = QtCore.QPoint(x_offset, y_offset)
                node.setPos(pos)
                x_offset += node.boundingRect().width() + hspace
                nodes_to_arrange.append(node)

        for edge in self.__edges:
            edge.adjust()

        self.update()

    def item_moved(self):
        """
        Called when an item in the graph has changed position.

        This method's job is to simply start the restart the main timer in case it is not
        running already. the timer is designed to stop when the graph stabilizes, and start
        once it is unstable again.
        """

        # if not self.__timer_id:
        #     self.__timer_id = self.startTimer(1000 / 25)

    def execute(self):
        """Traverse the graph starting from the root node and execute each node's function."""

        nodes_to_process = deque()
        nodes_to_process.append(self.__root_node)

        # As nodes are executed, keep track of their results (to pass to their outputs)
        node_results = {}

        # No cycle detection required since this is checked at initial build time

        while nodes_to_process:
            node = nodes_to_process.popleft()

            # Skip if the node has already been executed (if a node is an output of multiple
            # nodes, it will be added to the process list more than once)
            if node.id in node_results:
                continue

            # Ensure that all input nodes have executed before this node, and gather all input
            # node results to pass to this node
            inputs_ready = True
            input_data = {}
            for input_node in node.inputs:
                if not input_node.id in node_results:
                    inputs_ready = False
                    break

                node_data = node_results[input_node.id]
                # Merge the node data into the full input data
                # FIXME merge lists
                input_data.update(node_data)

            # Do not execute node if its inputs have not executed yet. Add it back to the list
            # of nodes to process once all inputs are ready
            if not inputs_ready:
                nodes_to_process.append(node)
                continue

            # Execute the node with all of its input data
            result = node.execute(input_data)
            # Store the result
            node_results[node.id] = result or {}
            # Add the node outputs to the list to process
            nodes_to_process.extend(node.outputs)
