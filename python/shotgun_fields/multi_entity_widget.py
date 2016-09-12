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
from sgtk.platform.qt import QtGui, QtCore

from .bubble_widget import BubbleEditWidget, BubbleWidget
from .entity_widget import EntityWidget
from .shotgun_field_meta import ShotgunFieldMeta
from .util import check_project_search_supported

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
global_search_completer = sgtk.platform.current_bundle().import_module("global_search_completer")


class MultiEntityWidget(EntityWidget):
    """
    Display a ``multi_entity`` field value as returned by the Shotgun API.
    """
    _DISPLAY_TYPE = "multi_entity"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A List of Shotgun entity dictionaries, each with keys for at
            least type, id, and name
        """
        return ", ".join([self._entity_dict_to_html(entity) for entity in value])

class MultiEntityEditorWidget(BubbleEditWidget):
    """
    Allows editing of a ``multi_entity`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "multi_entity"

    def add_entity(self, entity_dict):
        """
        Add an entity bubble to the widget.

        :param dict entity_dict: A dictionary of information about the entity
        :return: (int) unique id for the added entity

        The ``entity_dict`` must include the following fields::

          {
            "type": "Asset",
            "id": 12345,
            "name": "Teapot",
          }

        """

        # get a list of the current entity bubbles to see if the entity being
        # added is already in the list. if it is, remove it and re-add it to the
        # end of the list
        bubbles = self.get_bubbles()
        for bubble in bubbles:
            bubble_entity_dict = bubble.get_data()

            # see if the bubble matches the supplied entity dict
            if (bubble_entity_dict["type"] == entity_dict["type"] and
                bubble_entity_dict["id"] == entity_dict["id"]):
                # move the bubble to the end
                self.remove_bubble(bubble.id)
                self.add_entity(bubble_entity_dict)
                return

        # get an icon to display for the entity type
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(entity_dict["type"])

        # truncate the display name of the entity if necessary
        name = entity_dict["name"]
        display_name = name[0:22]
        if len(name) > 22:
            display_name += "..."

        # create a bubble widget to display the entity
        entity_bubble = BubbleWidget()
        entity_bubble.set_data(entity_dict)
        entity_bubble.set_image(entity_icon_url)
        entity_bubble.set_text(display_name)

        # return the unique id for the added bubble
        return self.add_bubble(entity_bubble)

    def focusInEvent(self, event):
        """
        Show the completer when the widget receives focus.

        :param event: The focus in event object
        :type event: :class:`~PySide.QtGui.QEvent`
        """

        # "remind" the completer what widget it operates on
        # apparently this is needed - see
        # http://doc.qt.io/qt-4.8/qt-tools-customcompleter-example.html
        self._completer.setWidget(self)

        if not self._completer.popup().isVisible():
            self._show_completer()
        super(MultiEntityEditorWidget, self).focusInEvent(event)

    def get_value(self):
        """
        Return a list of entity dicitionaries for the entity bubbles in the widget.

        :returns: A list of :obj:`dict` objects.
        :rtype: :obj:`list`
        """
        return [b.get_data() for b in self.get_bubbles()]

    def hideEvent(self, event):
        """
        Make sure the completer is hidden when the widget is.

        :param event: The hide event object
        :type event: :class:`~PySide.QtGui.QEvent`
        """
        self._hide_completer()
        super(MultiEntityEditorWidget, self).hideEvent(event)

    def keyPressEvent(self, event):
        """
        Handles user interaction with the widget via keyboard.

        - Ctrl+Enter and Ctrl+Return will trigger the ``value_changed`` signal to be emitted
        - Enter, Return, and Tab will attempt to add the current completer item

        :param event: The key press event.
        :type event: :class:`~PySide.QtGui.QEvent`
        """

        if event.key() in [
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return
        ] and event.modifiers() & QtCore.Qt.ControlModifier:
            self.value_changed.emit()
            event.ignore()
            return
        elif event.key() in [
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Tab,
        ]:
            entity_dict = self._completer.get_current_result()
            if not entity_dict:
                # nothing current, get the first result
                entity_dict = self._completer.get_first_result()

            if entity_dict:
                self.add_entity(entity_dict)
                self.clear_typed_text()
            event.ignore()
            return

        super(MultiEntityEditorWidget, self).keyPressEvent(event)

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization. Sets up the completer and
        valid types accepted by the widget.

        """

        sg_connection = self._bundle.sgtk.shotgun

        # TODO: remove this check and backward compatibility layer. added 09/16
        self._project_search_supported = check_project_search_supported(sg_connection)

        valid_types = {}

        # get this field's schema
        for entity_type in shotgun_globals.get_valid_types(self._entity_type, self._field_name):
            if entity_type == "Project" and not self._project_search_supported:
                # there is an issue querying Project entities via text_search
                # with older versions of SG. for now, don't restrict the editor
                 continue
            else:
                valid_types[entity_type] = []

        self._completer = global_search_completer.GlobalSearchCompleter()
        self._completer.set_bg_task_manager(self._bg_task_manager)
        self._completer.set_searchable_entity_types(valid_types)
        self._completer.setWidget(self)

        # connect the signals.
        self.textChanged.connect(self._on_text_changed)
        self._completer.entity_activated.connect(self._on_entity_activated)

    def _display_default(self):
        """
        Display the default value of the widget.
        """
        self.clear()

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        self.clear()
        for entity_dict in value:
            self.add_entity(entity_dict)

    def _hide_completer(self):
        """
        Convenience wrapper for hiding the completer popup.
        """
        self._completer.popup().hide()

    def _on_entity_activated(self, type, id, name):
        """
        When an entity is activated via the completer, add it to the widget.

        :param str type: The entity type
        :param int id: The entity's id
        :param str name: The name of the entity.
        """
        entity_dict = {"type": type, "id": id, "name": name}
        self._completer.popup().hide()
        self._completer.clear()
        self.clear_typed_text()
        self.add_entity(entity_dict)

    def _on_text_changed(self):
        """
        Show the copmleter as text is changing in the widget.
        """
        self._show_completer()

    def _show_completer(self):
        """
        Handles displaying the completer in the proper location relative to the cursor.
        """
        typed_text = self.get_typed_text()
        if self.isVisible() and typed_text:
            rect = self.cursorRect()
            rect.setWidth(300)
            rect.moveLeft(self.rect().left())
            rect.moveTop(rect.top() + 6)
            self._completer.setCompletionPrefix(typed_text)
            self._completer.complete(rect)
            self._completer.search(typed_text)

