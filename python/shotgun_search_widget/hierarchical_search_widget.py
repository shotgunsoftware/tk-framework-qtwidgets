# Copyright (c) 2015 Shotgun Software Inc.
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

search_completer = sgtk.platform.current_bundle().import_module(
    "search_completer"
)


class HierarchicalSearchWidget(ShotgunSearchWidget):
    """
    A QT Widget deriving from :class:`~PySide.QtGui.QLineEdit` that creates
    a hierarchical search input box with auto completion.

    :signal: ``node_activated(str, int, str, str, dict)`` - Fires when someone activates a
        node inside the search results. The parameters are ``type``, ``id``, ``name``,
        ``label path`` and ``incremental_paths``. If the node activated is not an entity,
        ``type`` and ``id`` will be ``None``.
    """

    # emitted when shotgun has been updated
    node_activated = QtCore.Signal(str, int, str, str, dict)

    def __init__(self, parent):
        """
        Uses the :class:``HierarchicalSearchCompleter`` as the completer for searching
        SG entities.

        :param parent: Qt parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        # first, call the base class and let it do its thing.
        super(HierarchicalSearchWidget, self).__init__(parent)

        # configure our popup completer
        self.setCompleter(search_completer.HierarchicalSearchCompleter(self))

        # forward the completer's node_selected signals
        self.completer().node_activated.connect(self.node_activated)

    def set_search_root(self, entity):
        """
        Allows to change the root of the search.

        :param dict entity: Entity to search under. If ``None``, the search will be done
            at the site level. Note that only project entities are supported at the moment.
        """
        self.completer().set_search_root(entity)
