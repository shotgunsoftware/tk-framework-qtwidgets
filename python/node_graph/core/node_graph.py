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
import os
import tempfile

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

        graph_begin_reset = QtCore.Signal()
        graph_end_reset = QtCore.Signal()
        graph_node_added = QtCore.Signal(Node)
        graph_node_removed = QtCore.Signal(Node)

    def __init__(self, bg_task_manager=None):
        """Initialize the node graph object."""

        self.__root_node = None
        self.__root_node_name = "Start"
        self.__nodes = {}
        self.__edges = []

        self.__notifier = self.Notifier()

        # NOTE exploring async options
        self.__executing_nodes = []
        self.__bg_task_manager = bg_task_manager
        # self.__bg_task_manager.task_completed.connect(self._on_background_task_completed)
        # self.__bg_task_manager.task_failed.connect(self._on_background_task_failed)
        # self.__bg_task_manager.task_group_finished.connect(
        #     self._on_background_task_group_finished
        # )

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
        self.__edges = []

    def build(self, data):
        """Build the graph given the data."""

        self.notifier.graph_begin_reset.emit()

        try:
            # Clear the graph first
            self.clear()

            # First create the super root node and add it to the graph's list of nodes
            self.__root_node = Node(self.ROOT_NODE_ID, {"name": self.__root_node_name})
            self.__nodes[self.__root_node.id] = self.__root_node

            # Create the nodes in the graph from the given data
            for data_id, data_value in data.items():
                self.add_node(data_id, data_value, add_edges=False)

            # Add edges from top-level nodes to the root
            for node_id, node in self.nodes.items():
                if node_id == self.ROOT_NODE_ID:
                    continue
                self.add_node_edges(node)

            # Last pass to add nodes from super root to top-level nodes
            for node_id, node in self.nodes.items():
                if node_id == self.ROOT_NODE_ID:
                    continue
                if not node.inputs:
                    # Add an edge to the super root node for top-level nodes
                    edge = self.__root_node.add_output(node)
                    self.__edges.append(edge)
        finally:
            self.notifier.graph_end_reset.emit()

    def add_node(self, node_id, node_data, add_edges=True):
        """Add a node to the graph."""

        # Check the node does not use a reserved id
        if node_id == self.ROOT_NODE_ID:
            raise self.NodeGraphError(
                "Cannot use id for node '{}' - reservered for graph root node.".format(
                    node_id
                )
            )

        # Check the node id is unique
        if node_id in self.nodes:
            raise self.NodeGraphError(
                "Cannot use id for node '{}' - not unique.".format(node_id)
            )

        # Create the node object and add it to the graph list of nodes
        node = Node(node_id, node_data)
        self.__nodes[node_id] = node

        if add_edges:
            self.add_node_edges(node)

        # NOTE we do not check for cycles here -- the execute method may need to handle cycles after all
        # since it might be a lot of maintenance to keep checking on any graph modification

        self.notifier.graph_node_added.emit(node)

        return node

    def add_node_edges(self, node):
        """Add the edges for the node."""

        # Add edges between the new node and its outputs
        output_node_ids = node.data.get("outputs", [])
        for output_node_id in output_node_ids:
            output_node = self.nodes.get(output_node_id)
            if output_node:
                edge = node.add_output(output_node)
                self.__edges.append(edge)

        # Add edges between the new node and its inputs
        input_node_ids = node.data.get("inputs", [])
        for input_node_id in input_node_ids:
            input_node = self.nodes.get(input_node_id)
            if input_node:
                edge = input_node.add_output(node)
                self.__edges.append(edge)

    def remove_node(self, node_id):
        """Remove the node from the graph."""

        node = self.nodes.get(node_id)
        if not node:
            return

        # Remove edges
        # NOTE need to implemente equality ops for Node and Edge to do it this way
        # for edge in node.edges:
        #     self.edges.remove(edge)
        i = 0
        while i < len(self.edges):
            edge = self.edges[i]
            if edge.input_node.id == node.id:
                self.edges.remove(edge)
                # TODO Also remove the edge from the node
                for node_edge in edge.output_node.edges:
                    if node_edge.input_node.id == node.id:
                        edge.output_node.edges.remove(node_edge)

            elif edge.output_node.id == node.id:
                self.edges.remove(edge)
                # TODO Also remove the edge from the node
                for node_edge in edge.input_node.edges:
                    if node_edge.output_node.id == node.id:
                        edge.input_node.edges.remove(node_edge)

            else:
                i += 1

        del self.nodes[node_id]

        # Notify to remove node and edge items from graph view
        self.notifier.graph_node_removed.emit(node)

    def execute(self):
        """
        Traverse the graph starting from the root node and execute each node's function.

        NOTE how do we keep this generic and not just for VRED?
        NOTE do not modify the current file unless the output is to save as current?
        NOTE if there are multiple outputs, we need to traverse the graph DFS, save temp file at the beginning and then copy to output

        Execute flow (with VRED as example):
            1. Start node must be an input node
                a. Can be either a scene graph node or a file (app context may affect what makes sense here, e.g. inside VRED we would always want the current file?)
            2a. If it is a file - load it
            2b. If it is a node - we are using current file (do nothing)
            3. For each output
                3a. Save current loaded file to temp location to work on (and to not modify the current file)
                3b. Execute output node function
                3c. Pass results to its output nodes and execute and continue until no more outputs
            4. If our last output node is a "write/publish" node then move our temp file to the specified output location
        """

        # # Our super root node does nto have a function other than indicating it is the start
        # input_nodes = self.__root_node.outputs
        # if not input_nodes:
        #     return

        # # TODO handle more than one input node?
        # input_node = input_nodes[0]

        # # For each of our outputs we will save a temp file to work on
        # for output_node in input_node.outputs:
        #     # TODO load if input file
        #     tmp_output_file = os.path.join(tempfile.gettempdir(), output_node.id, ".vpb")

        node_results = {}
        self.execute_depth_first_search(self.__root_node, node_results)

    def execute_depth_first_search(self, node, node_results):
        """Execute using Depth First Search."""

        if not node:
            return

        # Skip if the node has already been executed (if a node is an output of multiple
        # nodes, it will be added to the process list more than once)
        if node.id in node_results:
            return

        # Ensure that all input nodes have executed before this node, and gather all input
        # node results to pass to this node
        # inputs_ready = True
        input_data = {}
        for input_node in node.inputs:
            if not input_node.id in node_results:
                # inputs_ready = False
                # break
                return

            node_data = node_results[input_node.id]
            # Merge the node data into the full input data
            # FIXME merge lists
            input_data.update(node_data)

        # Do not execute node if its inputs have not executed yet. Add it back to the list
        # of nodes to process once all inputs are ready
        # if not inputs_ready:
        # nodes_to_process.append(node)
        # continue

        # Execute the node with all of its input data
        result = node.execute(input_data)

        # Store the result
        node_results[node.id] = result or {}

        # Add the node outputs to the list to process
        # nodes_to_process.extend(node.outputs)
        for output_node in node.outputs:
            self.execute_depth_first_search(output_node, node_results)

    def execute_breadth_first_search(self, root_node=None):
        """
        Execute using Breadth First Search.

        This is a more generic graph execution but it won't handle multple outputs.
        """

        root_node = root_node or self.__root_node

        nodes_to_process = deque()
        nodes_to_process.append(root_node)

        # As nodes are executed, keep track of their results (to pass to their outputs)
        node_results = {}

        # No cycle detection required since this is checked at initial build time
        # NOTE may need to add cycle detection back here

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

    # def execute(self):
    #     """Traverse the graph starting from the root node and execute each node's function."""

    #     # Clear the execution list first -- should not be doing more than one at once
    #     self.__executing_nodes = {}
    #     self.__executing_node_results = {}

    #     self.__executing_nodes_to_process = deque()
    #     # self.__executing_nodes_to_process.append(self.__root_node)

    #     self.__execute_async(self.__root_node)

    # def __execute_async(self, node):
    #     """
    #     """

    #     # nodes_to_process = deque()
    #     # nodes_to_process.append(root_node)

    #     # As nodes are executed, keep track of their results (to pass to their outputs)
    #     # node_results = {}

    #     # No cycle detection required since this is checked at initial build time
    #     # NOTE may need to add cycle detection back here

    #     # while self.__executing_nodes_to_process:
    #     #     node = self.__executing_nodes_to_process.popleft()

    #     # Skip if the node has already been executed (if a node is an output of multiple
    #     # nodes, it will be added to the process list more than once)
    #     if node.id in self.__executing_node_results:
    #         return

    #     # Skip if it is currently being executed
    #     for executing_node in self.__executing_nodes.values():
    #         if node.id == executing_node.id:
    #             return

    #     # Ensure that all input nodes have executed before this node, and gather all input
    #     # node results to pass to this node
    #     # inputs_ready = True
    #     input_data = {}
    #     for input_node in node.inputs:
    #         if not input_node.id in self.__executing_node_results:
    #             # inputs_ready = False
    #             # break
    #             return # Exit exec immediately as it is not ready to execute

    #         node_data = self.__executing_node_results[input_node.id]
    #         # Merge the node data into the full input data
    #         # FIXME merge lists
    #         input_data.update(node_data)

    #     # # Do not execute node if its inputs have not executed yet. Add it back to the list
    #     # # of nodes to process once all inputs are ready
    #     # if not inputs_ready:
    #     #     # self.__executing_nodes_to_process.append(node)
    #     #     # continue
    #     #     return

    #     #
    #     # TODO execute async with bg task manager
    #     #
    #     # Execute the node with all of its input data
    #     # result = node.execute(input_data)
    #     task_id = self.__bg_task_manager.add_task(
    #         node.execute,
    #         task_kwargs={"input_data": input_data},
    #         # group=self.TASK_GROUP_PROCESSED_FILES,
    #     )
    #     self.__executing_nodes[task_id] = node

    #     # # Store the result
    #     # node_results[node.id] = result or {}
    #     # # Add the node outputs to the list to process
    #     # nodes_to_process.extend(node.outputs)

    # def _on_background_task_completed(self, uid, group_id, result):
    #     """
    #     """

    #     if uid not in self.__executing_nodes:
    #         return

    #     node = self.__executing_nodes[uid]

    #     # Store the result
    #     self.__executing_node_results[node.id] = result or {}

    #     # Add the node outputs to the list to process
    #     # self.__executing_nodes_to_process.extend(node.outputs)
    #     for output_node in node.outputs:
    #         self.__execute_async(output_node)

    #     del self.__executing_nodes[uid]

    # def _on_background_task_failed(self, uid, group_id, msg, stack_trace):
    #     """
    #     """

    #     if uid not in self.__executing_nodes:
    #         return

    #     del self.__executing_nodes[uid]

    # def _on_background_task_group_finished(self, group_id):
    #     """
    #     """
