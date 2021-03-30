# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from tank.util import sgre as re

from .view_item_delegate import ViewItemDelegate


class ThumbnailViewItemDelegate(ViewItemDelegate):
    """
    A subclass of the ViewItemDelegate, where the thumbnail is the focus of the display, and
    is more compact (ideal for items with less text).
    """

    def __init__(self, parent=None):
        """
        Constructor

        Call the base constructor and set up properties specific to this delegate class.

        :param parent: The parent widget that will be used with this delegate.
        :type parent: :class:`sgtk.platform.qt.QtGui.QAbstractItemView`
        """

        super(ThumbnailViewItemDelegate, self).__init__(parent)

        # Default size
        self._thumbnail_size = QtCore.QSize(128, 128)
        self._text_document_margin = 5
        self._visible_lines = 2

    def sizeHint(self, option, index):
        """
        Override the base ViewItemDelegate method.

        The size hint is based on the thumbnail size. The width is set to the thumbnail
        width, plus the item padding. If the min_width property is set, the width will be
        at least the min_width. The height is set to the thumbnail height, plus the height
        of the text and item padding. Currently, the min_height property is not supported
        by this delegate.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The size hint for this index.
        :rtype: :class:`sgtk.platform.qt.QtCore.QSize`
        """

        view_option = QtGui.QStyleOptionViewItem(option)
        self.initStyleOption(view_option, index)

        width = max(self.thumbnail_width, self.min_width)

        # Get the full height of the item text.
        text_rect = self._get_text_rect(view_option, index)
        text_doc = self._get_text_document(view_option, index, text_rect, clip=False)
        text_height = text_doc.size().height()

        if self.get_value(index, self.thumbnail_role):
            # Item height is the thumbnail height plus the text height.
            height = self.thumbnail_height
            height += max(text_height, self._get_visible_lines_height(option))
        else:
            # No thumbnail, height is just the text height.
            height = text_height

        # Add item padding
        width += self.item_padding
        height += self.item_padding

        return QtCore.QSize(width, height)

    def _get_text(self, index, option=None, rect=None):
        """
        Override the base ViewItemDelegate method.

        Return the text data to display. The text data will be the data retrieved from the
        short_text_role. If the short_text_role is not defined, the base implementaiton
        will be called.

        :param index: The item model index.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: A list, where each item represents a text line in the item's whole text.
        :rtype: list<str>
        """

        if self.short_text_role:
            return self.get_display_values_list(index, self.short_text_role)

        return super(ThumbnailViewItemDelegate, self)._get_text(index)

    def _get_thumbnail_rect(self, option, index):
        """
        Override the base ViewItemDelegate method.

        Return the bounding rect for the item's thumbnail. The bounding rect will be
        positioned at the top of the option rect, span the full width and height will
        be set to the `thumbnail_size` property height. NOTE that the `min_height`
        property is ignored here.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The bounding rect for the item thumbnail.
        :rtype: :class:`sgtk.platform.qt.QtCore.QRect`
        """

        if not self.get_value(index, self.thumbnail_role):
            return QtCore.QRect()

        rect = QtCore.QRect(option.rect)
        width = max(self.thumbnail_size.width(), self.min_width)
        rect.setSize(QtCore.QSize(width, self.thumbnail_size.height()))

        return rect

    def _get_text_rect(self, option, index):
        """
        Override the base ViewItemDelegate method.

        Return the bounding rect for the item's text. The bounding rect will be
        positioned directly under the bounding rect of the thumbnail, span the
        full width and take up the remaining height of the option rect.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The bounding rect for the item text.
        :rtype: :class:`sgtk.platform.qt.QtCore.QRect`
        """

        if not self.get_value(index, self.thumbnail_role):
            return super(ThumbnailViewItemDelegate, self)._get_text_rect(option, index)

        rect = QtCore.QRect(option.rect)
        top_left = rect.topLeft()
        top_left.setY(top_left.y() + self.thumbnail_height)

        rect.setSize(QtCore.QSize(rect.width(), rect.height() - self.thumbnail_height))
        rect.moveTo(top_left)

        return rect
