# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui

from .bubble_widget import BubbleEditWidget, BubbleWidget
from .label_base_widget import ElidedLabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

from .ui import resources_rc

class TagsWidget(ElidedLabelBaseWidget):
    """
    Display a ``tag_list`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "tag_list"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param list value: A list of tag name strings
        """
        tag_strings = []
        for tag in value:
            tag_strings.append(
                "<img src='%s'>&nbsp;%s" % (
                    ":/qtwidgets-shotgun-fields/tag.png", tag
                )
            )

        return "&nbsp;".join(tag_strings)

class TagsEditorWidget(BubbleEditWidget):

    # TODO: The python API does not currently support add/remove/edit of tags.
    # Once the api supports tag updates, this class can be further fleshed out
    # to mimic the editing capabilities available in the web interface.

    # TODO: The following line is commented out so that the class is not
    # registered as a tag editor. Uncomment when tags are supported.
    #__metaclass__ = ShotgunFieldMeta
    #_EDITOR_TYPE = "tag_list"

    # TODO: some additional validation will need to happen to make sure a valid
    # tag was entered and that the user can create a tag if one does not exist.
    # A tag completer would also be useful if matching tag list could be queried
    # or made available via the cached schema.

    def add_tag(self, tag):
        """
        Add a tag bubble to the widget.

        :param str tag: The name of a tag to display
        :return: unique id for the added tag
        :rtype: :obj:`int`
        """

        # get a list of the current tag bubbles to see if the tag being
        # added is already in the list. if it is, remove it and re-add it to the
        # end of the list
        bubbles = self.get_bubbles()
        for bubble in bubbles:
            bubble_tag = bubble.get_data()

            # see if the bubble matches the supplied tag
            if tag == bubble_tag:
                # move the bubble to the end
                self.remove_bubble(bubble.id)
                self.add_tag(tag)
                return

        # create a bubble widget to display the tag
        tag_bubble = BubbleWidget()
        tag_bubble.set_data(tag)
        tag_bubble.set_image(":/qtwidgets-shotgun-fields/tag.png")
        tag_bubble.set_text(tag)
        tag_bubble_id = self.add_bubble(tag_bubble)

        # return the unique id for the added bubble
        return tag_bubble_id

    def get_value(self):
        """
        Return a list of tag names for the entity bubbles in the widget.

        :returns: A list of :obj:`str` objects.
        :rtype: :obj:`list`
        """
        return [b.get_data() for b in self.get_bubbles()]

    def keyPressEvent(self, event):
        """
        Handles user interaction with the widget via keyboard.

        - Enter, Return, Tab, Comma, and Space will cause the currently typed tag to be added.

        :param event: The key press event.
        :type event: :class:`~PySide.QtGui.QEvent`
        """

        if event.key() in [
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.Key_Comma,
            QtCore.Qt.Key_Space,
        ]:
            tag = self.get_typed_text()
            tag.strip()
            self.add_tag(tag)
            self.clear_typed_text()
            event.ignore()
            return

        super(TagsEditorWidget, self).keyPressEvent(event)

    def remove_tag(self, tag):
        """
        Removes the supplied tag bubble from the widget.

        :param str tag: The tag to remove
        """

        bubbles = self.get_bubbles()
        for bubble in bubbles:
            bubble_tag = bubble.get_data()
            if tag == bubble_tag:
                self.remove_bubble(bubble.id)
                return

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
        for tag in value:
            self.add_tag(tag)


