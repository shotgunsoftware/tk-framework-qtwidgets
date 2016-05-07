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

import sgtk

from .bubble_widget import BubbleEditWidget, BubbleWidget
from .entity_widget import EntityWidget

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


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

class MultiEntityEditorWidget(BubbleEditWidget):

    _EDITOR_TYPE = "multi_entity"

    def add_entity(self, entity_dict):

        bubbles = self.get_bubbles()
        for bubble in bubbles:
            bubble_entity_dict = bubble.get_data()
            if (bubble_entity_dict["type"] == entity_dict["type"] and
                bubble_entity_dict["name"] == entity_dict["name"]):
                # move the bubble to the end
                self.remove_bubble(bubble.id)
                self.add_entity(bubble_entity_dict)
                return

        entity_icon_url = shotgun_globals.get_entity_type_icon_url(entity_dict["type"])

        entity_bubble = BubbleWidget()
        entity_bubble.set_data(entity_dict)
        entity_bubble.set_image(entity_icon_url)
        entity_bubble.set_text(entity_dict["name"])

        entity_bubble_id = self.add_bubble(entity_bubble)

        return entity_bubble_id

    def _display_default(self):
        self.clear()

    def _display_value(self, value):
        self.clear()
        for entity_dict in value:
            self.add_entity(entity_dict)
