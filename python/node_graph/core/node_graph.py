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


class NodeGraph:
    """A class to represent a node graph."""

    # The id reserved for the super root node of the graph
    ROOT_NODE_ID = "__root_id__"

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

        self.__root_node = None
        self.__root_node_name = "Start"
        self.__nodes = {}
        self.__edges = []

        self.__search_method = self.SearchMethod.DepthFirstSearch
        self.__notifier = notifier

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

    @property
    def search_method(self):
        """Get or set the search method used ito traverse the graph."""
        return self.__search_method

    @search_method.setter
    def search_method(self, value):
        self.__search_method = value

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
            for item_id, item_data in data.items():
                node_data = item_data["node_data"]
                self.add_node(item_id, node_data)

            # Add edges for all nodes after they have all been created
            for item_id, item_data in data.items():
                if item_id == self.ROOT_NODE_ID:
                    continue
                node = self.__nodes[item_id]
                output_node_ids = item_data.get("output_node_ids", [])
                self.add_node_edges(node, output_node_ids)

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

    def add_node(self, node_id, node_data, output_node_ids=None):
        """Add a node to the graph."""

        output_node_ids = output_node_ids or []

        if node_id is None:
            # Auto generate a unique id for the node
            # TODO improve this
            node_id = f"__node_{len(self.nodes)}__"

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

        # if add_edges:
        self.add_node_edges(node, output_node_ids)

        # NOTE we do not check for cycles here -- the execute method may need to handle cycles after all
        # since it might be a lot of maintenance to keep checking on any graph modification

        self.notifier.graph_node_added.emit(node)

        return node

    def add_node_edges(self, node, output_node_ids):
        """Add the edges for the node."""

        # Add edges between the given node and its outputs
        for output_node_id in output_node_ids:
            output_node = self.nodes.get(output_node_id)
            if output_node:
                edge = node.add_output(output_node)
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

        if self.search_method.value == self.SearchMethod.DepthFirstSearch.value:
            node_results = {}
            self.execute_depth_first_search(self.__root_node, node_results)

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

        # Recursively execute the output nodes
        for output_node in node.outputs:

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
