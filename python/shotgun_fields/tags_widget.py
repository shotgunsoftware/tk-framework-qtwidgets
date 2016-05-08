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
Widget that represents the value of a tag_list field in Shotgun
"""

from sgtk.platform.qt import QtCore, QtGui

from .bubble_widget import BubbleEditWidget, BubbleWidget
from .label_base_widget import ElidedLabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

from .ui import resources_rc

class TagsWidget(ElidedLabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a tag_list field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "tag_list"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: List of Strings
        """
        tag_strings = []
        for tag in value:
            tag_strings.append(
                "<img src='%s'>&nbsp;%s" % (
                    ":/qtwidgets-shotgun-fields/tag.png", tag
                )
            )

        return "&nbsp;".join(tag_strings)

# XXX exclude this class form sphinx docs
class TagsEditorWidget(BubbleEditWidget):

    # TODO: The python API does not currently support add/remove/edit of tags.
    # Once the api supports tag updates, this class can be further fleshed out
    # to mimic the editing capabilities available in the web interface.

    # TODO: The following line is commented out so that the class is not
    # registered as a tag editor. Uncomment when tags are supported.
    #__metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "tag_list"

    # TODO: some additional validation will need to happen to make sure a valid
    # tag was entered and that the user can create a tag if one does not exist.
    # A tag completer would also be useful if matching tag list could be queried
    # or made available via the cached schema.

    def add_tag(self, tag):

        # remove the tag if it's already there and add it to the end
        bubbles = self.get_bubbles()
        for bubble in bubbles:
            bubble_tag = bubble.get_data()
            if tag == bubble_tag:
                # move the bubble to the end
                self.remove_bubble(bubble.id)
                self.add_tag(tag)
                return

        tag_bubble = BubbleWidget()
        tag_bubble.set_data(tag)
        tag_bubble.set_image(":/qtwidgets-shotgun-fields/tag.png")
        tag_bubble.set_text(tag)
        tag_bubble_id = self.add_bubble(tag_bubble)

        return tag_bubble_id

    def keyPressEvent(self, event):

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

        bubbles = self.get_bubbles()
        for bubble in bubbles:
            bubble_tag = bubble.get_data()
            if tag == bubble_tag:
                self.remove_bubble(bubble.id)
                return

    def _display_default(self):
        self.clear()

    def _display_value(self, value):
        self.clear()
        for tag in value:
            self.add_tag(tag)

    def get_value(self):
        return [b.get_data() for b in self.get_bubbles()]


