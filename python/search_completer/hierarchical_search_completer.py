# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .search_completer import SearchCompleter

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")


class HierarchicalSearchCompleter(SearchCompleter):
    """
    A standalone ``QCompleter`` class for matching SG entities to typed text.

    :signal: ``node_activated(str, int, str)`` - Fires when someone activates a
        node inside the search results. The parameters are ``type``, ``id``, ``name``,
        ``label path`` and ``incremental_paths``. If the node activated is not an entity,
        ``type`` and ``id`` will be ``None``.
    """

    # path label, entity type, entity id, name, incremental path
    node_activated = QtCore.Signal(str, int, str, str, dict)

    def __init__(self, parent=None):
        super(HierarchicalSearchCompleter, self).__init__(parent)
        self.set_search_root(self._bundle.context.project)

    def set_search_root(self, project_entity):
        """
        Allows to change the root of the search.

        :param dict project_entity: Project to search under. If ``None``, the search will be done
            at the site level.
        """
        if not project_entity:
            self._search_root = "/"
        else:
            self._search_root = "/Project/%d" % project_entity.get("id")

    def _set_item_delegate(self, popup, text):
        """
        Sets the item delegate for the popup widget.

        :param popup: Qt Popup widget receiving the delegate.
        :paarm text: Text from the current search.
        """
        # deferred import to help documentation generation.
        from .hierarchical_search_result_delegate import HierarchicalSearchResultDelegate
        self._delegate = HierarchicalSearchResultDelegate(popup, text)
        popup.setItemDelegate(self._delegate)

    def _launch_sg_search(self, text):
        """
        Called by the base class to kickstart the search process.
        """
        return self._sg_data_retriever.execute_nav_search_string(
            self._search_root, text
        )

    def _handle_search_results(self, data):
        """
        Called by the base class when the search results have come back from
        Shotgun.
        """
        matches = data["sg"]

        if len(matches) == 0:
            item = QtGui.QStandardItem("No matches found!")
            item.setData(self.MODE_NOT_FOUND, self.MODE_ROLE)
            self.model().appendRow(item)

        # insert new data into model
        for d in matches:
            item = QtGui.QStandardItem(d["label"])
            item.setData(self.MODE_RESULT, self.MODE_ROLE)

            item.setData(shotgun_model.sanitize_for_qt_model(d),
                         self.SG_DATA_ROLE)

            item.setIcon(self._pixmaps.no_thumbnail)

            if d["ref"]["type"] and d["ref"]["id"] and self._sg_data_retriever:
                uid = self._sg_data_retriever.request_thumbnail_source(
                    d["ref"]["type"],
                    d["ref"]["id"],
                    load_image=True
                )
                self._thumb_map[uid] = {"item": item}

            self.model().appendRow(item)

    def get_result(self, model_index):
        """
        Returns an item from the result list.

        :param model_index: :class:`QtModelIndex` of the result to retrieve.

        :returns: Returns a dictionary of the match.
            For example::
                {
                    "label": "bunny_020",
                    "incremental_path": [
                        "/Project/65",
                        "/Project/65/Shot",
                        "/Project/65/Shot/sg_sequence/Sequence/5"
                    ],
                    "path_label": "Shots",
                    "ref": {
                        "id": 5,
                        "type": "Sequence"
                    },
                    "project_id": 65
                }
        """
        mode = shotgun_model.get_sanitized_data(model_index, self.MODE_ROLE)
        if mode == self.MODE_RESULT:
            # get the payload
            data = shotgun_model.get_sanitized_data(model_index, self.SG_DATA_ROLE)
            return data
        else:
            return None

    def _on_select(self, model_index):
        """
        Called by the base class when something was selected in the pop-up. Emits
        the ``node_activated`` event.

        :param model_index: :class:`QtModelIndex` of the item that was selected.
        """

        data = self.get_result(model_index)
        if data:
            # Let it be known that something was picked.
            self.node_activated.emit(
                data["ref"]["type"], data["ref"]["id"], data["label"],
                data["path_label"],
                data["incremental_path"]
            )
