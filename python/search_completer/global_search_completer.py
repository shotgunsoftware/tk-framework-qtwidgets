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

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from .search_completer import SearchCompleter


class GlobalSearchCompleter(SearchCompleter):
    """
    A standalone :class:`PySide.QtGui.QCompleter` class for matching SG entities to typed text.

    :signal: ``entity_selected(str, int)`` - Provided for backward compatibility.
      ``entity_activated`` is emitted at the same time with an additional ``name``
      value. Fires when someone selects an entity inside the search results. The
      returned parameters are entity ``type`` and entity ``id``.

    :signal: ``entity_activated(str, int, str)`` - Fires when someone activates an
      entity inside the search results. Essentially the same as ``entity_selected``
      only the parameters returned are ``type``, ``id`` **and** ``name``.

    :modes: ``MODE_LOADING, MODE_NOT_FOUND, MODE_RESULT`` - Used to identify the
        mode of an item in the completion list

    :model role: ``MODE_ROLE`` - Stores the mode of an item in the completion
        list (see modes above)

    :model role: ``SG_DATA_ROLE`` - Role for storing shotgun data in the model
    """

    # emitted when shotgun has been updated
    entity_selected = QtCore.Signal(str, int)
    entity_activated = QtCore.Signal(str, int, str)

    def __init__(self, parent=None):
        """
        :param parent: Parent widget
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        super(GlobalSearchCompleter, self).__init__(parent)

        # the default entity search criteria. The calling code can override these
        # criterial by calling ``set_searchable_entity_types``.
        self._entity_search_criteria = {
            "Asset": [],
            "Shot": [],
            "Task": [],
            "HumanUser": [["sg_status_list", "is", "act"]],
            "Group": [],
            "ClientUser": [["sg_status_list", "is", "act"]],
            "ApiUser": [],
            "Version": [],
            "PublishedFile": [],
        }

    def get_result(self, model_index):
        """
        Return the entity data for the supplied model index or None if there is
        no data for the supplied index.

        :param model_index: The index of the model to return the result for.
        :type model_index: :class:`~PySide.QtCore.QModelIndex`

        :return: The entity dict for the supplied model index.
        :rtype: :obj:`dict`: or ``None``
        """

        # make sure that the user selected an actual shotgun item.
        # if they just selected the "no items found" or "loading please hold"
        # items, just ignore it.
        mode = shotgun_model.get_sanitized_data(model_index, self.MODE_ROLE)
        if mode == self.MODE_RESULT:

            # get the payload
            data = shotgun_model.get_sanitized_data(model_index, self.SG_DATA_ROLE)

            # Example of data stored in the data role:
            #
            # {'status': 'vwd',
            #  'name': 'bunny_010_0050_comp_v001',
            #  'links': ['Shot', 'bunny_010_0050'],
            #  'image': 'https://xxx',
            #  'project_id': 65,
            #  'type': 'Version',
            #  'id': 99}

            # NOTE: this data format differs from what is typically returned by
            # the shotgun python-api. this data may be formalized at some point
            # but for now, only expose the minimum information.

            return {
                "type": data["type"],
                "id": data["id"],
                "name": data["name"],
            }
        else:
            return None

    def set_searchable_entity_types(self, types_dict):
        """
        Specify a dictionary of entity types with optional search filters to
        limit the breadth of the widget's search.

        Use this method to override the default searchable entity types
        dictionary which looks like this::

          {
            "Asset": [],
            "Shot": [],
            "Task": [],
            "HumanUser": [["sg_status_list", "is", "act"]],    # only active users
            "Group": [],
            "ClientUser": [["sg_status_list", "is", "act"]],   # only active users
            "ApiUser": [],
            "Version": [],
            "PublishedFile": [],
          }

        :param types_dict: A dictionary of searchable types with optional filters

        """
        self._entity_search_criteria = types_dict

    def _set_item_delegate(self, popup, text):
        """
        Sets an item delegate for the completer's popup.

        :param popup: Popup instance from the completer.
        :type popup: :class:`~PySide.QtGui.QAbstractItemView`

        :param str text: Text used for completion.
        """
        # deferred import to help documentation generation.
        from .global_search_result_delegate import GlobalSearchResultDelegate
        self._delegate = GlobalSearchResultDelegate(popup, text)
        popup.setItemDelegate(self._delegate)

    def _launch_sg_search(self, text):
        """
        Launches a search on the Shotgun server.

        :param str text: Text to search for.

        :returns: The :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever`'s job id.
        """

        # constrain by project in the search
        project_ids = []

        if len(self._entity_search_criteria.keys()) == 1 and \
           "Project" in self._entity_search_criteria:
            # this is a Project-only search. don't restrict by the current project id
            pass
        elif self._bundle.context.project:
            project_ids.append(self._bundle.context.project["id"])

        return self._sg_data_retriever.execute_text_search(
            text,
            self._entity_search_criteria,
            project_ids
        )

    def _on_select(self, model_index):
        """
        Fires when an item in the completer is selected. This will emit an entity_selected signal
        for the global search widget

        :param model_index: QModelIndex describing the current item
        """
        data = self.get_result(model_index)
        if data:
            self.entity_selected.emit(data["type"], data["id"])
            self.entity_activated.emit(data["type"], data["id"], data["name"])

    def _handle_search_results(self, data):
        """
        Populates the model associated with the completer with the data coming back from Shotgun.

        :param dict data: Data received back from the job sent to the
            :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever` in :method:``_launch_sg_search``.
        """
        matches = data["sg"]["matches"]

        if len(matches) == 0:
            item = QtGui.QStandardItem("No matches found!")
            item.setData(self.MODE_NOT_FOUND, self.MODE_ROLE)
            self.model().appendRow(item)

        # insert new data into model
        for d in matches:
            item = QtGui.QStandardItem(d["name"])
            item.setData(self.MODE_RESULT, self.MODE_ROLE)

            item.setData(shotgun_model.sanitize_for_qt_model(d),
                         self.SG_DATA_ROLE)

            item.setIcon(self._pixmaps.no_thumbnail)

            if d.get("image") and self._sg_data_retriever:
                uid = self._sg_data_retriever.request_thumbnail(
                    d["image"],
                    d["type"],
                    d["id"],
                    "image",
                    load_image=True
                )
                self._thumb_map[uid] = {"item": item}

            self.model().appendRow(item)
