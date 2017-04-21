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


class GlobalSearchResultDelegate(SearchResultDelegate):
    """
    Delegate which renders search match entries in the global
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
        from .global_search_completer import GlobalSearchCompleter

        icon = shotgun_model.get_sanitized_data(model_index, QtCore.Qt.DecorationRole)
        if icon:
            thumb = icon.pixmap(512)
            widget.set_thumbnail(thumb)
        else:
            # probably won't hit here, but just in case, use default/empty
            # thumbnail
            widget.set_thumbnail(self._pixmaps.no_thumbnail)

        data = shotgun_model.get_sanitized_data(model_index, GlobalSearchCompleter.SG_DATA_ROLE)
        # Example of data stored in the data role:
        # {'status': 'vwd',
        #  'name': 'bunny_010_0050_comp_v001',
        #  'links': ['Shot', 'bunny_010_0050'],
        #  'image': 'https://xxx',
        #  'project_id': 65,
        #  'type': 'Version',
        #  'id': 99}

        entity_type_display_name = shotgun_globals.get_type_display_name(data["type"])

        content = ""
        et_url = shotgun_globals.get_entity_type_icon_url(data["type"])

        underlined_name = self._underline_search_term(data["name"])

        if et_url:
            # present thumbnail icon and name
            content += "<img src='%s'/>&nbsp;&nbsp;<b style='color: rgb(48, 167, 227)';>%s</b>" % (
                et_url, underlined_name
            )
        else:
            # present type name name
            content += "%s" % underlined_name

        content += "<br>%s" % entity_type_display_name

        links = data["links"]
        # note users return weird data so ignore it.
        if links and links[0] != "" and links[0] != "HumanUser" and links[0] != "ClientUser":
            underlined_link = self._underline_search_term(links[1])
            # there is a referenced entity
            et_url = shotgun_globals.get_entity_type_icon_url(links[0])
            if et_url:
                # present thumbnail icon and name
                content += " on <img align=absmiddle src='%s'/>  %s" % (et_url, underlined_link)
            else:
                # present type name name
                link_entity_type = links[0]
                content += " on %s %s" % (shotgun_globals.get_type_display_name(link_entity_type), underlined_link)

        widget.set_text(content)
