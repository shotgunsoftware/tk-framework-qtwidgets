# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import copy

# from .edge import Edge


class Node:
    """The base node class."""

    def __init__(self, node_id, node_data):
        """
        Initialize the node.

        :param parent: The parent of the node.
        :type parent: QGraphicsItem
        """

        # TODO remove this - data should be processed into properties
        self.__data = node_data

        self.__id = node_id
        self.__allowed_inputs = node_data.get("allowed_inputs", True)
        self.__allowed_outputs = node_data.get("allowed_outputs", True)
        self.__exec_func = node_data.get("exec_func", None)
        self.__post_exec_func = node_data.get("post_exec_func", None)
        self.__pre_output_exec_func = node_data.get("pre_output_exec_func", None)
        self.__post_output_exec_func = node_data.get("post_output_exec_func", None)

        # NOTE we may want to create a class to handle settings objects
        self.__settings = copy.deepcopy(node_data.get("settings", {}))

        # NOTE do we need to store inputs/outputs here?
        self.__input_nodes = []
        self.__output_nodes = []

        self.__is_executing = False

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def id(self):
        """Return the unique id of the node."""
        return self.__id

    @property
    def data(self):
        """Get the data pertaining to this node."""
        return self.__data

    @property
    def inputs(self):
        """Get the list of input node ids."""
        return self.__input_nodes

    @property
    def outputs(self):
        """Get the list of output node ids."""
        return self.__output_nodes

    @property
    def input_nodes(self):
        """Get the list of input nodes."""
        return self.__input_nodes

    @property
    def output_nodes(self):
        """Get the list of output nodes."""
        return self.__output_nodes

    @property
    def allowed_inputs(self):
        """
        Get the number of allowed inputs, if any.

        If this property is False, then no outputs are allowed.
        If this property is True, then any number of outputs allowed.
        If this property is an integer, then that number of outputs allowed.
        """
        return self.__allowed_inputs

    @property
    def allowed_outputs(self):
        """
        Get the number of allowed outputs, if any.

        If this property is False, then no outputs are allowed.
        If this property is True, then any number of outputs allowed.
        If this property is an integer, then that number of outputs allowed.
        """
        return self.__allowed_outputs

    @property
    def settings(self):
        """Get the current settings values."""
        return self.__settings

    @property
    def is_executing(self):
        """Return True if the node is running its execute function."""
        return self.__is_executing

    # ----------------------------------------------------------------------------------------
    # Public methods

    def add_output(self, output_node, add_reverse_input=True):
        """Add an output node to this node and connect it with an edge."""

        # First check that a new output can be added
        if isinstance(self.allowed_outputs, bool):
            if not self.allowed_outputs:
                # TODO custom exception
                raise Exception("Node does not allow any outputs.")
        elif isinstance(self.allowed_outputs, int):
            if len(self.output_nodes) + 1 > self.allowed_outputs:
                raise Exception("Node has maximum outputs already")
        else:
            assert False, "Unsupported value tpe for allowed_outputs property"

        # Add the output to the list
        self.__output_nodes.append(output_node)

        if add_reverse_input:
            output_node.add_input(self, add_reverse_output=False)

    def add_input(self, input_node, add_reverse_output=True):
        """Add an input node to this node andd connect it with an edge."""

        # First check that a new input can be added
        if isinstance(self.allowed_inputs, bool):
            if not self.allowed_inputs:
                # TODO custom exception
                raise Exception("Node does not accept any inputs.")
        elif isinstance(self.allowed_inputs, int):
            if len(self.input_nodes) + 1 > self.allowed_inputs:
                raise Exception("Node already has maximum inputs..")
        else:
            assert False, "Unsuuported value tpe for allowed_inputs property"

        # Add the input to the list
        self.__input_nodes.append(input_node)

        if add_reverse_output:
            input_node.add_output(self, add_reverse_output=False)

    def execute(self, input_data=None):
        """Execute the node's function, if it has one."""

        # TODO report errors if found / visually

        self.__is_executing = True

        try:
            if not self.__exec_func:
                return

            print("Executing...", self.data.get("name", self.id))
            return self.__exec_func(input_data, self.settings)
        finally:
            self.__is_executing = False

    def post_execute(self, input_data=None):
        """Execute the node's post execute function, if it has one."""

        if not self.__post_exec_func:
            return

        print("Post executing...", self.data.get("name", self.id))
        return self.__post_exec_func(input_data, self.settings)

    def pre_output_exec(self, input_data, output_node):
        """Run the node's prepare function before output node is executed."""

        if not self.__pre_output_exec_func:
            return

        print(f"\tPre output exec: {output_node.id}")
        return self.__pre_output_exec_func(input_data, output_node)

    def post_output_exec(self, input_data, output_node):
        """Run the node's clean up function after the output node has finished executing."""

        if not self.__post_output_exec_func:
            return

        print(f"\tPost output exec: {output_node.id}")
        return self.__post_output_exec_func(input_data, output_node)
