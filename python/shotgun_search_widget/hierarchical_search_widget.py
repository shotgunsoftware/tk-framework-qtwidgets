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
        # When the node is activated it queues an event to put the selection into the line edit.
        # Queueing the event like this ensures we clean up the line edit after.
        # Taken from:
        # http://stackoverflow.com/questions/11865129/fail-to-clear-qlineedit-after-selecting-item-from-qcompleter
        self.completer().node_activated.connect(self.clear, QtCore.Qt.QueuedConnection)

        self.show_entities_only = True
        self.search_root = sgtk.platform.current_bundle().context.project

    def _get_search_root(self):
        """
        The entity under which the search will be done. If ``None``, the search will be done
        for the whole site.

        The entity is a ``dict`` with keys ``id`` and ``type``. Note that only ``Project`` entities
        are supported at the moment.
        """
        return self.completer().search_root

    def _set_search_root(self, entity):
        """
        See getter documentation.
        """
        self.completer().search_root = entity

    search_root = property(_get_search_root, _set_search_root)

    def _get_show_entities_only(self):
        """
        Indicates if only entities will be shown in the search results.

        If set to ``True``, only entities will be shown.
        """
        self.completer().show_entities_only

    def _set_show_entities_only(self, is_set):
        """
        See getter documentation.
        """
        self.completer().show_entities_only = is_set

    show_entities_only = property(_get_show_entities_only, _set_show_entities_only)

    def _get_seed_entity_field(self):
        """
        The seed entity to use when searching for entity.

        Can be ``PublishedFile.entity`` or ``Version.entity``.
        """
        return self.completer().seed_entity_field

    def _set_seed_entity_field(self, seed_entity_field):
        """
        See setter documentation.
        """
        self.completer().seed_entity_field = seed_entity_field

    seed_entity_field = property(_get_seed_entity_field, _set_seed_entity_field)
