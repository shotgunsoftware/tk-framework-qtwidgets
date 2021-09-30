# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.
from time import time

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

        self._thumbnail_size = QtCore.QSize(164, 128)
        self.thumbnail_position = (self.TOP,)

    def sizeHint(self, option, index):
        """
        Override the base ViewItemDelegate method.

        The size hint is based on the thumbnail size. The width is set to the thumbnail
        width, plus the item padding. If the min_width property is set, the width will be
        at least the min_width. The height is set to the thumbnail height, plus the height
        of the text and item padding. Currently, the min_height property is not supported
        by this delegate.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The size hint for this index.
        :rtype: :class:`sgtk.platform.qt.QtCore.QSize`
        """

        view_option = QtGui.QStyleOptionViewItem(option)
        self.initStyleOption(view_option, index)

        # The size hint will mainly be based off of the thumbnail rect.
        thumbnail_rect = self._get_thumbnail_rect(option, index)

        # Get the full height of the item text.
        text_rect = self._get_text_rect(view_option, index)
        text_doc, _ = self._get_text_document(view_option, index, text_rect, clip=False)
        text_height = text_doc.size().height()

        width = max(thumbnail_rect.width(), self.min_width)
        height = thumbnail_rect.height() + max(
            text_height, self._get_visible_lines_height(option)
        )

        # Add padding
        width += self.item_padding.left + self.item_padding.right
        width += self.thumbnail_padding.left + self.thumbnail_padding.right

        height += self.item_padding.top + self.item_padding.bottom
        height += self.text_padding.top + self.text_padding.bottom
        if thumbnail_rect.isValid():
            height += self.thumbnail_padding.top + self.thumbnail_padding.bottom

        return QtCore.QSize(width, height)

    def _get_loading_rect(self, option, index):
        """
        Override the base ViewItemDelegate method.

        Return the bounding rect for the item's loading icon. An invalid rect will be
        returned if the item is not in a loading state. The bounding rect will be positioned
        to the right in the option rect, and centered vertically.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The bounding rect for the item's loading indicator. The rect will be invalid
                 if there is no loading indicatorto display.
        :rtype: :class:`sgtk.platform.qt.QtCore.QRect`
        """

        if not self.loading_role:
            return QtCore.QRect()

        loading = self.get_value(index, self.loading_role)
        if not loading:
            return QtCore.QRect()

        center = QtCore.QPoint(
            option.rect.left() + option.rect.width() / 2 - self.icon_size.width() / 2,
            option.rect.top() + option.rect.height() / 2 - self.icon_size.height() / 2,
        )

        return QtCore.QRect(center, self.icon_size)

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
            return [
                self._get_header_text(index, option, rect)
            ] + self.get_display_values_list(index, self.short_text_role)

        return super(ThumbnailViewItemDelegate, self)._get_text(index, option, rect)

    def _get_thumbnail_rect(self, option, index, thumbnail=None):
        """
        Override the base ViewItemDelegate method.

        Return the bounding rect for the item's thumbnail. The bounding rect will be
        positioned at the top of the option rect, span the full width and height will
        be set to the `thumbnail_size` property height. NOTE that the `min_height`
        property is ignored here.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The bounding rect for the item thumbnail.
        :rtype: :class:`sgtk.platform.qt.QtCore.QRect`
        """

        if thumbnail is None:
            thumbnail = self._get_thumbnail(index)

        if not thumbnail:
            return QtCore.QRect()

        rect = QtCore.QRect(option.rect)
        width = max(self.thumbnail_size.width(), self.min_width)
        # Account for extra text padding
        width += max(0, self.text_padding.left - self.thumbnail_padding.left)
        width += max(0, self.text_padding.right - self.thumbnail_padding.right)

        rect.setSize(QtCore.QSize(width, self.thumbnail_size.height()))
        rect.adjust(
            self.thumbnail_padding.left,
            self.thumbnail_padding.top,
            -self.thumbnail_padding.right,
            -self.thumbnail_padding.bottom,
        )

        return rect

    def _get_text_rect(self, option, index):
        """
        Override the base ViewItemDelegate method.

        Return the bounding rect for the item's text. The bounding rect will be
        positioned directly under the bounding rect of the thumbnail, span the
        full width and take up the remaining height of the option rect.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The bounding rect for the item text.
        :rtype: :class:`sgtk.platform.qt.QtCore.QRect`
        """

        if not self._get_thumbnail(index):
            return super(ThumbnailViewItemDelegate, self)._get_text_rect(option, index)

        rect = QtCore.QRect(option.rect)
        top_left = rect.topLeft()
        top_left.setY(top_left.y() + self.thumbnail_height)

        rect.setSize(QtCore.QSize(rect.width(), rect.height() - self.thumbnail_height))
        rect.moveTo(top_left)

        rect.adjust(
            self.text_padding.left,
            self.text_padding.top,
            -self.text_padding.right,
            -self.text_padding.bottom,
        )

        return rect
