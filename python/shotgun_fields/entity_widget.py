# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Widget that represents the value of an entity field in Shotgun
"""
import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .label_base_widget import ElidedLabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
global_search_widget = sgtk.platform.current_bundle().import_module("global_search_widget")


class EntityWidget(ElidedLabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display an entity field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "entity"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A Shotgun entity dictionary containing at least keys for type, int, and name
        """
        return self._entity_dict_to_html(value)

    def _entity_dict_to_html(self, value):
        """
        Translate the entity dictionary to html that can be displayed in a
        :class:`~PySide.QtGui.QLabel`.

        :param value: The entity dictionary to convert to html
        :type value: An entity dictionary containing at least the name, type, and id keys
        """
        str_val = value["name"]

        if self._bundle.sgtk.shotgun_url.endswith("/"):
            url_base = self._bundle.sgtk.shotgun_url
        else:
            url_base = "%s/" % self._bundle.sgtk.shotgun_url

        link_color = sgtk.constants.SG_STYLESHEET_CONSTANTS["SG_HIGHLIGHT_COLOR"]

        entity_url = "%sdetail/%s/%d" % (url_base, value["type"], value["id"])
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(value["type"])
        str_val = (
            "<span><img src='%s'>&nbsp;"
            "<a href='%s'><font color='%s'>%s</font></a></span>"
             % (entity_icon_url, entity_url, link_color, str_val)
        )

        return str_val

class EntityEditorWidget(global_search_widget.GlobalSearchWidget):

    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "entity"
    _IMMEDIATE_APPLY = True

    #def _begin_edit(self):


    def setup_widget(self):
        self.set_bg_task_manager(self._bg_task_manager)

        valid_types = {}

        # get this field's schema
        for entity_type in shotgun_globals.get_valid_types(self._entity_type, self._field_name):
            # Can't search for project?
            # XXX why can't
            if entity_type == "Project":
                continue
            # XXX default filters?
            valid_types[entity_type] = []

        self.set_searchable_entity_types(valid_types)

    def _display_default(self):
        self.clear()

    def _display_value(self, value):
        self.clear()
        self.setText(str(value["name"]))

