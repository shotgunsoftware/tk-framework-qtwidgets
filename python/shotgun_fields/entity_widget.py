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
from .label_base_widget import LabelBaseWidget
from .widget_metaclass import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class EntityWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display an entity field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _FIELD_TYPE = "entity"

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
        entity_url = "%sdetail/%s/%d" % (self._bundle.sgtk.shotgun_url, value["type"], value["id"])
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(value["type"])
        str_val = "<img src='%s'><a href='%s'>%s</a>" % (entity_icon_url, entity_url, str_val)
        return str_val
