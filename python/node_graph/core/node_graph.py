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
from enum import Enum, unique, auto

from .node import Node
from .edge import Edge


class NodeGraph:
    """A class to represent a node graph."""

    class NodeGraphError(Exception):
        """Custom exception class to throw for graph related errors."""

    class NodeGraphCycleError(Exception):
        """Custom exception class to throw when a cycle in the graph is detected."""

    @unique
    class SearchMethod(Enum):
        """Enum class for node graph search methods."""

        DepthFirstSearch = auto()
        BreadthFirstSearch = auto()

    def __init__(self, notifier=None, bg_task_manager=None):
        """Initialize the node graph object."""

        self.__root_nodes = []
        self.__nodes = {}
        self.__edges = []

        self.__search_method = self.SearchMethod.DepthFirstSearch
        self.__notifier = notifier

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def search_method(self):
        """Get or set the search method used ito traverse the graph."""
        return self.__search_method

    @search_method.setter
    def search_method(self, value):
        self.__search_method = value

    @property
    def root_nodes(self):
        """Get the top-level nodes in the graph."""
        return self.__root_nodes

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

        self.__root_nodes = []
        self.__nodes = {}
        self.__edges = []

    def build(self, data):
        """Build the graph given the data."""

        self.notifier.graph_begin_reset.emit()

        try:
            # Clear the graph first
            self.clear()

            # Create the nodes in the graph from the given data
            for item_id, item_data in data.items():
                node_data = item_data["node_data"]
                self.add_node(item_id, node_data)

            # Add edges for all nodes after they have all been created
            for item_id, item_data in data.items():
                # if item_id == self.ROOT_NODE_ID:
                #     continue
                node = self.__nodes[item_id]
                output_node_ids = item_data.get("output_node_ids", [])
                # self.add_node_edges(node, output_node_ids)
                for output_node_id in output_node_ids:
                    output_node = self.nodes.get(output_node_id)
                    if output_node:
                        self.add_edge(node, output_node)

            # Last pass to keep track of all top-level root nodes
            for node in self.nodes.values():
                if not node.inputs:
                    self.__root_nodes.append(node)
        finally:
            self.notifier.graph_end_reset.emit()

    # def add_node(self, node_id, node_data, output_node_ids=None):
    def add_node(self, node_id, node_data, is_root=False):
        """Add a node to the graph."""

        # output_node_ids = output_node_ids or []

        if node_id is None:
            # Auto generate a unique id for the node
            # TODO improve this
            node_id = f"__node_{len(self.nodes)}__"

        # Check the node id is unique
        if node_id in self.nodes:
            raise self.NodeGraphError(
                "Cannot use id for node '{}' - not unique.".format(node_id)
            )

        # Create the node object and add it to the graph list of nodes
        node = Node(node_id, node_data)
        self.__nodes[node_id] = node

        if is_root:
            self.__root_nodes.append(node)

        self.notifier.graph_node_added.emit(node)

        return node

    def add_edge(self, input_node, output_node):
        """Add an edge to the node graph."""

        if not isinstance(input_node, Node):
            # Assume we have the id instead
            input_node = self.nodes.get(input_node)
            if not input_node:
                raise Exception("Invalid input node passed")

        if not isinstance(output_node, Node):
            # Assume we have the id instead
            output_node = self.nodes.get(output_node)
            if not output_node:
                raise Exception("Invalid output node passed")

        # Keep track of input/output nodes on the nodes themselves
        # NOTE this will throw an exception if not able to add input/output. TODO error handling?
        input_node.add_output(output_node)

        edge = Edge(input_node, output_node)
        self.__edges.append(edge)

        self.notifier.graph_edge_added.emit(edge.input_node, edge.output_node)

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
                # Remove node from input to the connecting edge node
                edge.output_node.input_nodes.remove(node)
                self.edges.remove(edge)

            elif edge.output_node.id == node.id:
                # Remove node from output to the connecting edge node
                edge.input_node.output_nodes.remove(node)
                self.edges.remove(edge)

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

        if self.search_method.value == self.SearchMethod.DepthFirstSearch.value:
            # Execute each sub tree within the node graph (node graph can have multiple trees)
            for root_node in self.root_nodes:
                node_results = {}
                self.execute_depth_first_search(root_node, node_results)

        elif self.search_method.value == self.SearchMethod.DepthFirstSearch.value:
            self.execute_breadth_first_search()

        else:
            raise self.NodeGraphError("Unsupported graph search method")

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
                return

            node_data = node_results[input_node.id]
            # Merge the node data into the full input data. For list values, first merge the values
            # into node_data, since node_data will overwrite input_data
            for key, value in node_data.items():
                if isinstance(value, list):
                    value.extend(input_data.get(key, []))
            input_data = {**input_data, **node_data}

        # Execute the node with all of its input data
        result = node.execute(input_data)
        # Store the result
        node_results[node.id] = result or {}

        if node.data.get("type") == "condition":
            # Logical operator to choose which output to execute

            # The result of the logical node execute will be the output index to execute. If
            # result is not an int, we will stop execution
            if not isinstance(result, int):
                outputs_to_execute = []
            elif 0 <= result < len(node.outputs):
                outputs_to_execute = [node.outputs[result]]
                # HACK forward the previous node's result to the outputs (not the logical node's result)
                node_results[node.id] = input_data or {}
            else:
                raise self.NodeGraphError("Logical node not set up correctly")

        else:
            # Execute all output nodes
            outputs_to_execute = node.outputs

        # Recursively execute outputs
        # for output_node in node.outputs:
        for output_node in outputs_to_execute:

            # Run the pre-exec output function and update the node results with the data
            # returned by the prepare function
            prepare_result = node.pre_output_exec(result, output_node)
            if prepare_result:
                node_results[node.id].update(prepare_result)

            # Recursively execute the node outputs
            self.execute_depth_first_search(output_node, node_results)

            # Run the post-exec output function, pass in the prepare result
            node.post_output_exec(prepare_result, output_node)

        # Pass the result of the node's execute function to its post exec method
        node.post_execute(result)

    def execute_breadth_first_search(self, root_nodes=None):
        """
        Execute using Breadth First Search.

        This is a more generic graph execution but it won't handle multple outputs.
        """

        root_nodes = root_nodes or self.root_nodes

        # Execute each sub tree in the node graph
        for root_node in root_nodes:
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
