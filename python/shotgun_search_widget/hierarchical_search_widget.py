# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore

from .shotgun_search_widget import ShotgunSearchWidget

search_completer = sgtk.platform.current_bundle().import_module("search_completer")


class HierarchicalSearchWidget(ShotgunSearchWidget):
    """
    A QT Widget deriving from :class:`~PySide.QtGui.QLineEdit` that creates
    a hierarchical search input box with auto completion.

    If defaults to searching inside the current context's project and to only show entities.

    :signal: ``node_activated(str, int, str, str, list)`` - Fires when someone activates a
        node inside the search results. The parameters are ``type``, ``id``, ``name``,
        ``label path`` and ``incremental_paths``. If the node activated is not an entity,
        ``type`` and ``id`` will be ``None``.
    """

    # emitted when shotgun has been updated
    node_activated = QtCore.Signal(str, int, str, str, list)

    def __init__(self, parent):
        """
        Uses the :class:`~search_completer.HierarchicalSearchCompleter` as the completer for searching
        SG entities.

        :param parent: Qt parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        # first, call the base class and let it do its thing.
        super(HierarchicalSearchWidget, self).__init__(parent)

        # configure our popup completer
        self.setCompleter(search_completer.HierarchicalSearchCompleter(self))

        # forward the completer's node_selected signals
        self.completer().node_activated.connect(self.node_activated.emit)

        self.show_entities_only = True
        self.search_root = sgtk.platform.current_bundle().context.project

    @property
    def search_root(self):
        """
        The entity under which the search will be done. If ``None``, the search will be done
        for the whole site.

        The entity is a ``dict`` with keys ``id`` and ``type``. Note that only ``Project`` entities
        are supported at the moment.
        """
        return self.completer().search_root

    @search_root.setter
    def search_root(self, entity):
        """
        See getter documentation.
        """
        self.completer().search_root = entity

    @property
    def show_entities_only(self):
        """
        Indicates if only entities will be shown in the search results.

        If set to ``True``, only entities will be shown.
        """
        self.completer.show_entities_only

    @show_entities_only.setter
    def show_entities_only(self, is_set):
        """
        See getter documentation.
        """
        self.completer().show_entities_only = is_set
