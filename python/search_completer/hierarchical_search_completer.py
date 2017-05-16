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
from sgtk.platform.qt import QtCore, QtGui

from .search_completer import SearchCompleter

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")


class HierarchicalSearchCompleter(SearchCompleter):
    """
    A standalone :class:`PySide.QtGui.QCompleter` class for matching SG entities to typed text.

    If defaults to searching inside the current context's project and to only show entities.

    :signal: ``node_activated(str, int, str, str, list)`` - Fires when someone activates a
        node inside the search results. The parameters are ``type``, ``id``, ``name``,
        ``label_path`` and ``incremental_path``. If the node activated is not an entity,
        ``type`` and ``id`` will be ``None``.

    :modes: ``MODE_LOADING, MODE_NOT_FOUND, MODE_RESULT`` - Used to identify the
        mode of an item in the completion list

    :model role: ``MODE_ROLE`` - Stores the mode of an item in the completion
        list (see modes above)

    :model role: ``SG_DATA_ROLE`` - Role for storing shotgun data in the model
    """

    # path label, entity type, entity id, name, incremental path
    node_activated = QtCore.Signal(str, int, str, str, list)

    def __init__(self, parent=None):
        """
        :param parent: Parent widget
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        super(HierarchicalSearchCompleter, self).__init__(parent)
        self.search_root = self._bundle.context.project
        self.show_entities_only = True
        self.seed_entity_field = "PublishedFile.entity"

    def _get_search_root(self):
        """
        The entity under which the search will be done. If ``None``, the search will be done
        for the whole site.

        The entity is a ``dict`` with keys ``id`` and ``type``. Note that only ``Project`` entities
        are supported at the moment.
        """
        return self._search_root

    def _set_search_root(self, entity):
        """
        See getter documentation.
        """
        self._search_root = entity

    search_root = property(_get_search_root, _set_search_root)

    def _get_show_entities_only(self):
        """
        Indicates if only entities will be shown in the search results.

        If set to ``True``, only entities will be shown.
        """
        return self._show_entities_only

    def _set_show_entities_only(self, is_set):
        """
        See getter documentation.
        """
        self._show_entities_only = is_set

    show_entities_only = property(_get_show_entities_only, _set_show_entities_only)

    def _get_seed_entity_field(self):
        """
        The seed entity to use when searching for entity.

        Can be ``PublishedFile.entity`` or ``Version.entity``.
        """
        return self._seed_entity_field

    def _set_seed_entity_field(self, seed_entity_field):
        """
        See setter documentation.
        """
        self._seed_entity_field = seed_entity_field

    seed_entity_field = property(_get_seed_entity_field, _set_seed_entity_field)

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
        Launches a search on the Shotgun server.

        :param str text: Text to search for.

        :returns: The :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever`'s job id.
        """
        # FIXME: Ideally we would use the nav_search_entity endpoint to compute the path to the root.
        # Unfortunately there is a bug a the moment that prevents this.
        if not self._search_root:
            root_path = "/"
        else:
            root_path = "/Project/%d" % self._search_root.get("id")

        return self._sg_data_retriever.execute_nav_search_string(
            root_path, text, self._seed_entity_field
        )

    def _handle_search_results(self, data):
        """
        Populates the model associated with the completer with the data coming back from Shotgun.

        :param dict data: Data received back from the job sent to the
            :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever` in :method:``_launch_sg_search``.
        """
        data_matches = data["sg"]

        # When showing only entities, skip entries that aren't.
        if self._show_entities_only:
            data_matches = filter(
                lambda x: x["ref"]["type"] is not None and x["ref"]["id"] is not None,
                data_matches
            )

        if len(data_matches) == 0:
            item = QtGui.QStandardItem("No matches found!")
            item.setData(self.MODE_NOT_FOUND, self.MODE_ROLE)
            self.model().appendRow(item)

        # Payload looks like:
        # [
        #     {
        #         "label": "bunny_020",
        #         "incremental_path": [
        #             "/Project/65",
        #             "/Project/65/Shot",
        #             "/Project/65/Shot/sg_sequence/Sequence/5"
        #         ],
        #         "path_label": "Shots",
        #         "ref": {
        #             "id": 5,
        #             "type": "Sequence"
        #         },
        #         "project_id": 65
        #     },
        #     ...
        # ]

        # insert new data into model
        for data in data_matches:

            item = QtGui.QStandardItem(data["label"])
            item.setData(self.MODE_RESULT, self.MODE_ROLE)

            item.setData(shotgun_model.sanitize_for_qt_model(data),
                         self.SG_DATA_ROLE)

            item.setIcon(self._pixmaps.no_thumbnail)

            data_type = data["ref"]["type"]
            data_id = data["ref"]["id"]
            if data_type and data_id and self._sg_data_retriever:
                uid = self._sg_data_retriever.request_thumbnail_source(
                    data_type, data_id, load_image=True
                )
                self._thumb_map[uid] = {"item": item}

            self.model().appendRow(item)

    def get_result(self, model_index):
        """
        Returns an item from the result list.

        Here's an example::

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

        :param model_index: The index of the model to return the result for.
        :type model_index: :class:`~PySide.QtCore.QModelIndex`

        :return: The ``dict`` for the supplied model index.
        :rtype: ``dict`` or ``None``
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
