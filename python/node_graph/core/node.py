# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from .edge import Edge


class Node:
    """The base node class."""

    def __init__(self, node_id, node_data):
        """
        Initialize the node.

        :param parent: The parent of the node.
        :type parent: QGraphicsItem
        """

        self.__id = node_id
        self.__data = node_data
        self.__exec_func = node_data.get("exec_func", None)

        # NOTE we may want to create a class to handle settings objects
        self.__settings = node_data.get("settings", {})

        self.__edges = []
        self.__input_nodes = []
        self.__output_nodes = []

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
    def edges(self):
        """Get the list of the node's edges."""
        return self.__edges

    @property
    def inputs(self):
        """Get the list of input nodes."""
        return self.__input_nodes

    @property
    def outputs(self):
        """Get the list of output nodes."""
        return self.__output_nodes

    @property
    def settings(self):
        """Get the current settings values."""
        return self.__settings

    # ----------------------------------------------------------------------------------------
    # Public methods

    def add_output(self, output_node, add_reverse_input=True):
        """Add an output node to this node and connect it with an edge."""

        edge = Edge(self, output_node)
        self.__edges.append(edge)
        self.__output_nodes.append(output_node)

        if add_reverse_input:
            output_node.add_input(self, add_reverse_output=False)

        return edge

    def add_input(self, input_node, add_reverse_output=True):
        """Add an input node to this node andd connect it with an edge."""

        edge = Edge(input_node, self)
        self.__edges.append(edge)
        self.__input_nodes.append(input_node)

        if add_reverse_output:
            input_node.add_output(self, add_reverse_output=False)

        return edge

    def execute(self, input_data=None):
        """Execute the node's function, if it has one."""

        print("Executing...", self.data.get("name", self.id))

        if not self.__exec_func:
            return

        return self.__exec_func(input_data, self.settings)
