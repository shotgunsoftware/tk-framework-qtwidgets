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

from .node import Node

# TODO remove
from sgtk.platform.qt import QtCore


class NodeGraph:
    """A class to represent a node graph."""

    # The id reserved for the super root node of the graph
    ROOT_NODE_ID = "__root_id__"

    class NodeGraphError(Exception):
        """Custom exception class to throw for graph related errors."""

    class NodeGraphCycleError(Exception):
        """Custom exception class to throw when a cycle in the graph is detected."""

    # TODO move class out to separate file to remove qt dep
    class Notifier(QtCore.QObject):
        """Class to emit signals around node graph operations."""

        build_begin = QtCore.Signal()
        build_finished = QtCore.Signal()

    def __init__(self):
        """Initialize the node graph object."""

        self.__root_node = None
        self.__root_node_name = "Start"
        self.__nodes = {}
        self.__edges = []

        self.__notifier = self.Notifier()

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def root_node_name(self):
        """Get or set the super root node display name."""
        return self.__root_node_name

    @root_node_name.setter
    def root_node_name(self, value):
        self.__root_node_name = value

    @property
    def root_node(self):
        """Get the super root node of the graph."""
        return self.__root_node

    @property
    def nodes(self):
        """Get the mapping of node id to node objects in the graph."""
        return self.__nodes

    @property
    def edges(self):
        """Return the list of edges in the graph."""
        return self.__edges

    @property
    def notifier(self):
        """ "Get the notifier object"""
        return self.__notifier

    # ----------------------------------------------------------------------------------------
    # Public methods

    def clear(self):
        """Clear the graph."""

        self.__root_node = None
        self.__nodes = {}

    def build(self, data):
        """Build the graph given the data."""

        self.notifier.build_begin.emit()

        try:
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

            # First create the super root node and add it to the graph's list of nodes
            self.__root_node = Node(self.ROOT_NODE_ID, {"name": self.__root_node_name})
            self.__nodes[self.__root_node.id] = self.__root_node

            # Create the nodes in the graph from the given data
            for data_id, data_value in data.items():
                if data_id == self.ROOT_NODE_ID:
                    raise self.NodeGraphError(
                        "Cannot use id for node '{}' - reservered for graph root node.".format(
                            data_id
                        )
                    )

                if data_id in node_ids:
                    raise self.NodeGraphError(
                        "Cannot use id for node '{}' - not unique.".format(data_id)
                    )

                # Create the node object
                node = Node(data_id, data_value)
                self.__nodes[data_id] = node

                # Process its outputs to create edges
                output_node_ids = data_value.get("outputs", [])
                for output_node_id in output_node_ids:
                    edges.append((data_id, output_node_id))
                    edge_graph.setdefault(data_id, []).append(output_node_id)
                    child_nodes.add(output_node_id)

            # Add edges to the nodes, while checking for cycles
            for edge_data in edges:
                input_node = self.nodes.get(edge_data[0])
                output_node = self.nodes.get(edge_data[1])

                # Ensure adding edge does not introduce a cycle in the graph. Detect cycle by
                # traversing the edge graph, if we can find our way back to the input node,
                # then there is a cycle. NOTE this approach is simple and could be optimized
                node_ids = edge_graph.get(output_node.id)
                while node_ids:
                    node_id = node_ids.pop()
                    if node_id == input_node.id:
                        raise self.NodeGraphCycleError("Detected cycle in node graph.")
                    node_ids.extend(edge_graph.get(node_id, []))

                edge = input_node.add_output(output_node)
                self.__edges.append(edge)

            # Add edges from top-level nodes to the root
            for node_id, node in self.nodes.items():
                if node_id == self.ROOT_NODE_ID:
                    continue
                if node_id in child_nodes:
                    continue

                edge = self.__root_node.add_output(node)
                self.__edges.append(edge)
        finally:
            self.notifier.build_finished.emit()

    def execute(self, root_node=None):
        """Traverse the graph starting from the root node and execute each node's function."""

        root_node = root_node or self.__root_node

        nodes_to_process = deque()
        nodes_to_process.append(root_node)

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
