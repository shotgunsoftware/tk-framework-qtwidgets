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


class GlobalSearchWidget(ShotgunSearchWidget):
    """
    A QT Widget deriving from :class:`~PySide.QtGui.QLineEdit` that creates
    a global search input box with auto completion.

    :signal: ``entity_selected(str, int)`` - Fires when someone selects an entity inside
            the search results. The returned parameters are entity type and entity id.

    :signal: ``entity_activated(str, int, str)`` - Fires when someone selects an
        entity inside the search results. Similar to ``entity_selected``, with
        the addition of the ``name`` of the activated entity being supplied.
    """

    # emitted when shotgun has been updated
    entity_selected = QtCore.Signal(str, int)
    entity_activated = QtCore.Signal(str, int, str)

    def __init__(self, parent):
        """
        Uses the :class:`~search_completer.GlobalSearchCompleter` as the completer for searching
        SG entities.

        :param parent: Qt parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        """

        # first, call the base class and let it do its thing.
        super(GlobalSearchWidget, self).__init__(parent)

        # configure our popup completer
        self.setCompleter(search_completer.GlobalSearchCompleter(self))
        # forward the completer's activated/selected signals
        self.completer().entity_selected.connect(self.entity_selected.emit)
        self.completer().entity_activated.connect(self.entity_activated.emit)
        # When the node is activated it queues an event to put the selection into the line edit.
        # Queueing the event like this ensures we clean up the line edit after.
        # Taken from:
        # http://stackoverflow.com/questions/11865129/fail-to-clear-qlineedit-after-selecting-item-from-qcompleter
        # Only need to listen to one of the two events as both are always emitted by the completer.
        self.completer().entity_activated.connect(self.clear, QtCore.Qt.QueuedConnection)

    def set_searchable_entity_types(self, types_dict):
        """
        Specify a dictionary of entity types with optional search filters to
        limit the breadth of the widget's search.

        See the documentation for `GlobalSearchCompleter.set_searchable_entity_types`
        for the default values if this method is not called on the widget.

        :param types_dict: A dictionary of searchable types with optional filters
        """

        self.completer().set_searchable_entity_types(types_dict)
