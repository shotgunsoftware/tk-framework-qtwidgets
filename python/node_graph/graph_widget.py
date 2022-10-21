# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .node import Node
from .edge import Edge


class GraphWidget(QtGui.QGraphicsView):
    """A widget to display a node graph."""

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

        # TODO end node?
        self.__root_node = Node({"name": "Start"}, self)
        self.add_node("root", self.__root_node)

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
        self.__root_node = Node({"name": "Start"}, self)
        self.add_node("root", self.__root_node)

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
        # Keep track of child nodes to determine which nodes are top-level, which will need an
        # edge added to the root node
        child_nodes = set()

        # Create the nodes in the graph
        for data_id, data_value in data.items():
            node = Node(data_value, self)
            self.add_node(data_id, node)

            output_node_ids = data_value.get("outputs", [])
            for output_node_id in output_node_ids:
                edges.append((data_id, output_node_id))
                child_nodes.add(output_node_id)

        # Add edges to the nodes
        for edge_data in edges:
            input_node = self.nodes.get(edge_data[0])
            output_node = self.nodes.get(edge_data[1])
            # edge = Edge(input_node, output_node)
            edge = input_node.add_output(output_node)
            self.add_edge(edge)

        # Add edges from top-level nodes to the root
        for node_id, node in self.nodes.items():
            # TODO store the node id in the Node object
            if node_id == "root":
                continue

            if node_id in child_nodes:
                continue

            edge = self.__root_node.add_output(node)
            self.add_edge(edge)

    def arrange_tree(self):
        """Arrange the node graph in a viewable format."""

        # print(self.sceneRect())

        # Set the starting root position to the top middle
        # pos_x = self.sceneRect().width() / 2 - self.__root_node.sceneBoundingRect().width() / 2
        # pos_y = self.sceneRect().y()
        pos_x = 0
        pos_y = 0
        pos = QtCore.QPoint(pos_x, pos_y)
        # pos = self.mapFromScene(pos)
        self.__root_node.setPos(pos)

        # Then draw its children below in a tree-like structure
        hspace = 10
        vspace = 50
        nodes_to_arrange = [self.__root_node]
        while nodes_to_arrange:
            parent = nodes_to_arrange.pop()
            nodes = parent.outputs
            # y_offset = parent.scenePos().y() + parent.sceneBoundingRect().height() + vspace
            y_offset = parent.pos().y() + parent.boundingRect().height() + vspace

            # First we need to calculate the level width to center the level of nows
            # level_width = sum([node.sceneBoundingRect().width() for node in nodes]) + sum([hspace] * len(nodes)) - hspace
            level_width = (
                sum([node.boundingRect().width() for node in nodes])
                + sum([hspace] * len(nodes))
                - hspace
            )
            # x_offset = (parent.scenePos().x() + parent.sceneBoundingRect().width()/2) - level_width/2
            x_offset = (
                parent.pos().x() + parent.boundingRect().width() / 2
            ) - level_width / 2

            for node in nodes:
                pos = QtCore.QPoint(x_offset, y_offset)
                # pos = self.mapFromScene(pos)
                node.setPos(pos)
                # x_offset += node.sceneBoundingRect().width() + hspace
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

        # TODO nodes wtih multiple inputs need to wait for all of their inputs

        nodes = self.__root_node.outputs
        input_data = self.__root_node.execute()
        nodes_to_process = [(nodes, input_data)]

        while nodes_to_process:
            nodes, input_data = nodes_to_process.pop()
            for node in nodes:
                result = node.execute(input_data)
                if node.outputs:
                    nodes_to_process.append((node.outputs, result))
