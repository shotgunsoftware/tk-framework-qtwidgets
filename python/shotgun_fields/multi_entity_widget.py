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
Widget that represents the value of a multi_entity field in Shotgun
"""
from .entity_widget import EntityWidget, EntityEditorWidget


class MultiEntityWidget(EntityWidget):
    """
    Inherited from a :class:`~EntityWidget`, this class is able to
    display a multi_entity field value as returned by the Shotgun API.
    """
    _DISPLAY_TYPE = "multi_entity"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A List of Shotgun entity dictionaries, each with keys for at least type, id, and name
        """
        return ", ".join([self._entity_dict_to_html(entity) for entity in value])

class MultiEntityEditorWidget(EntityEditorWidget):

    _EDITOR_TYPE = "multi_entity"