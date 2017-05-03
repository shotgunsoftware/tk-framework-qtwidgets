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

from .search_result_delegate import SearchResultDelegate

# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


views = sgtk.platform.current_bundle().import_module("views")


class HierarchicalSearchResultDelegate(SearchResultDelegate):
    """
    Delegate which renders search match entries in the hierarhical
    search completer.
    """

    def _render_result(self, widget, model_index):
        """
        Renders a result from the model into the provided widget.

        :param widget: Widget used to render the result.
        :type widget: ``SearchResultWidget``

        :param model_index: Index of the item to render.
        :type model_index: :class:`~PySide.QtCore.QModelIndex`
        """
        from .hierarchical_search_completer import HierarchicalSearchCompleter

        icon = shotgun_model.get_sanitized_data(model_index, QtCore.Qt.DecorationRole)
        if icon:
            thumb = icon.pixmap(512)
            widget.set_thumbnail(thumb)
        else:
            # probably won't hit here, but just in case, use default/empty
            # thumbnail
            widget.set_thumbnail(self._pixmaps.no_thumbnail)

        data = shotgun_model.get_sanitized_data(model_index, HierarchicalSearchCompleter.SG_DATA_ROLE)
        # Example of data stored in the data role:
        # {
        #     "path_label": "Assets > Character",
        #     "incremental_path": [
        #         "/Project/65",
        #         "/Project/65/Asset",
        #         "/Project/65/Asset/sg_asset_type/Character",
        #         "/Project/65/Asset/sg_asset_type/Character/id/734"
        #     ],
        #     "project_id": 65,
        #     "ref": {
        #         "type": "Asset",
        #         "id": 734
        #     },
        #     "label": "Bunny"
        # },

        if data["ref"]["type"]:
            et_url = shotgun_globals.get_entity_type_icon_url(data["ref"]["type"])
        else:
            et_url = None

        underlined_label = self._underline_search_term(data["label"])

        # present type name name
        if et_url:
            content = "<img src='%s'/>&nbsp;&nbsp;<b style='color: rgb(48, 167, 227)';>%s</b>" % (
                et_url, underlined_label
            )
        else:
            content = underlined_label

        content += "<br>%s" % data["path_label"]

        widget.set_text(content)
