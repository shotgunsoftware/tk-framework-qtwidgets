# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from sgtk.platform.qt import QtCore

from ...core.edge import Edge
from ...core.node import Node


class NodeGraphNotifier(QtCore.QObject):
    """Class to emit signals for node graph operations."""

    # Signal emitted before the node graph is about to reset
    graph_begin_reset = QtCore.Signal()
    # Signal emitted after the node graph has been reset
    graph_end_reset = QtCore.Signal()

    # Signal emitted after a node object has been added to the node graph
    graph_node_added = QtCore.Signal(Node)
    # Signal emitted after a node object has been removed from the node graph
    graph_node_removed = QtCore.Signal(Node)

    # Signal emitted after an edge object has been added to the node graph
    graph_edge_added = QtCore.Signal(Node, Node)
    # Signal emitted after an edge object has been removed from the node graph
    graph_edge_removed = QtCore.Signal(Node, Node)
