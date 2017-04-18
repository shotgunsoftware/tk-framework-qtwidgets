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

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from .search_completer import SearchCompleter


class GlobalSearchCompleter(SearchCompleter):
    """
    A standalone ``QCompleter`` class for matching SG entities to typed text.

    :signal: ``entity_selected(str, int)`` - Provided for backward compatibility.
      ``entity_activated`` is emitted at the same time with an additional ``name``
      value. Fires when someone selects an entity inside the search results. The
      returned parameters are entity ``type`` and entity ``id``.

    :signal: ``entity_activated(str, int, str)`` - Fires when someone activates an
      entity inside the search results. Essentially the same as ``entity_selected``
      only the parameters returned are ``type``, ``id`` **and** ``name``.

    :modes: ``MODE_LOADING, MODE_NOT_FOUND, MODE_RESULT`` - Used to identify the
        mode of an item in the completion list

    :model role: ``SG_DATA_ROLE`` - Role for storing shotgun data in the model
    :model role: ``MODE_ROLE`` - Stores the mode of an item in the completion
        list (see modes above)

    """

    def __init__(self, parent=None):
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

    def _launch_sg_search(self, text):

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
