# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.


class Edge:
    """A class to represent an edge connecting two nodes in a graph."""

    def __init__(self, input_node, output_node):
        """Initialize the edge object."""

        self.__input_node = input_node
        self.__output_node = output_node

    # ----------------------------------------------------------------------------------------
    # Properties

    @property
    def input_node(self):
        """Get the source node of this edge (the start point)."""
        return self.__input_node

    @input_node.setter
    def input_node(self, value):
        """Get the source node of this edge (the start point)."""
        self.__input_node = value

    @property
    def output_node(self):
        """Get the destination node of this edge (the end point)."""
        return self.__output_node

    @output_node.setter
    def output_node(self, value):
        """Get the destination node of this edge (the start point)."""
        self.__output_node = value
