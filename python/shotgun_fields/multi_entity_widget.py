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
from sgtk.platform.qt import QtGui, QtCore

from .bubble_widget import BubbleEditWidget, BubbleWidget
from .entity_widget import EntityWidget
from .shotgun_field_meta import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
global_search_completer = sgtk.platform.current_bundle().import_module("global_search_completer")


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

    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "multi_entity"

    def setup_widget(self):

        valid_types = {}

        # get this field's schema
        for entity_type in shotgun_globals.get_valid_types(self._entity_type, self._field_name):
            # Can't search for project?
            # XXX why can't
            if entity_type == "Project":
                continue
            # XXX default filters for some types?
            valid_types[entity_type] = []

        self._completer = global_search_completer.GlobalSearchCompleter()
        self._completer.set_bg_task_manager(self._bg_task_manager)
        self._completer.set_searchable_entity_types(valid_types)
        self._completer.setWidget(self)

        self.textChanged.connect(self._on_text_changed)

        self._completer.entity_activated.connect(self._on_entity_activated)

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

    def _on_entity_activated(self, entity):
        self._completer.popup().hide()
        self.clear_typed_text()
        self.add_entity(entity)

    def _on_text_changed(self):

        if self.isVisible():
            typed_text = self.get_typed_text()

            rect = self.cursorRect()
            rect.setWidth(self.width())
            rect.moveLeft(self.rect().left())
            rect.moveTop(rect.top() + 6)
            self._completer.complete(rect)
            self._completer.search(typed_text)




