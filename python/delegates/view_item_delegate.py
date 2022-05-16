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
from tank_vendor import six

utils = sgtk.platform.current_bundle().import_module("utils")

DEBUG_PAINT = False


class ViewItemDelegate(QtGui.QStyledItemDelegate):
    """
    A generic delegate to display items in a view.
    """

    # Positions for actions. Non-floating actions will adjust the content to
    # fit inline (e.g. not floating on top)
    POSITIONS = [
        "float-top-left",
        "float-top-right",
        "float-bottom-left",
        "float-bottom-right",
        "float-left",
        "float-right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
        "left",
        "right",
        "top",
        "bottom",
        "center",
    ]
    # Enum for the POSITIONS
    (
        FLOAT_TOP_LEFT,
        FLOAT_TOP_RIGHT,
        FLOAT_BOTTOM_LEFT,
        FLOAT_BOTTOM_RIGHT,
        FLOAT_LEFT,
        FLOAT_RIGHT,
        TOP_LEFT,
        TOP_RIGHT,
        BOTTOM_LEFT,
        BOTTOM_RIGHT,
        LEFT,
        RIGHT,
        TOP,
        BOTTOM,
        CENTER,
    ) = range(len(POSITIONS))

    class Padding(object):
        """
        Convenience class structure to store padding values.
        """

        def __init__(self, top, right, bottom, left):
            """
            Create the Padding object.

            :param top: The top padding value.
            :type top: int
            :param right: The right padding value.
            :type right: int
            :param bottom: The bottom padding value.
            :type bottom: int
            :param left: The left padding value.
            :type left: int
            """

            self.top = top
            self.right = right
            self.bottom = bottom
            self.left = left

        @classmethod
        def new(cls, padding):
            """
            Factory method to create a padding object with equal padding all around.
            """

            return cls(padding, padding, padding, padding)

    def __init__(self, view=None):
        """
        ViewItemDelegate constructor. Sets the default values.

        :param view: The view that this delegate will be used with.
        :type view: :class:`sgkt.platform.qt.QtGui.QAbstractItemView`
        """

        super(ViewItemDelegate, self).__init__(view)

        # Store the view widget to fall back on for older versions of Qt, where the QStyleOption does not
        # have a widget or styleObject property
        self._view = view

        # The item data model roles used to retrieve the item's data to display. See ViewItemRolesMixin for
        # more details about the item data roles.
        self._thumbnail_role = QtCore.Qt.DecorationRole
        self._header_role = None
        self._subtitle_role = None
        self._text_role = QtCore.Qt.DisplayRole
        self._short_text_role = None
        self._icon_role = None
        self._expand_role = None
        self._width_role = None
        self._height_role = None
        self._loading_role = None
        self._separator_role = None

        # The number of visible lines to show (e.g. text will be cut off to this defined number of lines)
        self._visible_lines = -1

        # The default qss to apply to the text document style sheet
        self._document_style_sheet = ""

        # Turn on text eliding, if False, text will be wrapped
        self._elide_text = True
        self._elide_header = True

        # Fix the item's width and height. These will be ignored if set to None. When set to -1, these will
        # expand to the full available space.
        self._item_width = None
        self._item_height = None
        # The minimum width and height for the item rect. These will essentially be ignored if less than 0
        self._min_width = -1
        self._min_height = -1

        # Fix the item's thumbnail size
        self._thumbnail_size = QtCore.QSize()
        # Set this value to scale the thumbnail size as the item height changes.
        self._thumbnail_scale_value = 1.5
        # Positioning of the thumbnail withint the available thumbnail rect. Empty tuple will default
        # to center the the thumbnail.
        self.thumbnail_position = ()
        # The extent used to convert a QIcon to QPixmap
        self._pixmap_extent = 512
        # The size used for icons
        self._icon_size = QtCore.QSize(18, 18)
        # This is the percentage value used to calculate the maximum badge icon height (e.g. badge
        # icon is rendered over a rect, if that rect height is 100 and the `badge_height_pct` is 0.5,
        # then the badge icon maximum height will be 50). Note that badge icons will only be scaled
        # down to fit, not scaled up if the icon size is smaller than the max height.
        self._badge_height_pct = 1.0 / 3.0

        # Button padding and margin values
        self._action_item_margin = 7
        self._button_padding = 4
        # Text document margin
        self._text_document_margin = 0
        # Padding around the whole item rect
        self._item_padding = self.Padding.new(2)
        self._text_padding = self.Padding.new(8)
        self._thumbnail_padding = self.Padding.new(0)

        # Text alignment (TOP | BOTTOM | CENTER). NOTE this aligns the text within the text bounding rect,
        # meaning that the text block will be aligned within the available text area, but text itself will
        # remain left-aligned. To implement aligning the text itself, a custom QTextDocumentLayout class
        # is required. There is another limitation to text horizontal alignment when there is a header
        # and/or subtitle present; horizontal alignment will have no effect since the header and subtitle
        # cause the text block to span the full available text bounding rect width.
        self._text_rect_halign = self.LEFT
        self._text_rect_valign = self.TOP

        # Font to set on the QTextDocument. If None, the font from the QStyleOptionViewItem will be used.
        self._font = None

        # Radius values for rounding item and thumbnail rects.
        self._item_x_radius = 4.0
        self._item_y_radius = 4.0
        self._thumbnail_x_radius = 4.0
        self._thumbnail_y_radius = 4.0

        # The pen used to draw the thumbnail (add a border around the pixmap rect).
        self._thumbnail_pen = QtCore.Qt.NoPen
        # The pen used to paint the background (the background brush is customized through the model data
        # role BackgroundRole). The pen is responsible for rendering a border around the item rect.
        self._background_pen = QtCore.Qt.NoPen
        # The brush and pen used to draw the loading indicator.
        self._loading_pen = QtCore.Qt.NoPen
        self._loading_brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 100))
        # The brush used to paint the selection. The palette highlight brush will be used if not set.
        self._selection_brush = None
        # The brush used to paint the item separator, if there is one.
        self._separator_brush = QtCore.Qt.NoBrush

        # Enable painting selection on hover
        self._show_hover_selection = True
        # Enable showing tooltips when text is clipped
        self._show_text_tooltip = True
        # Override the QStandardItem object toolitp
        self._override_item_tooltip = True

        # Values used to draw the animated loading image
        self._seconds_per_spin = 3
        self._spin_arc_len = 300

        # The actions for the item
        self._actions = {}
        # The cursor shape that will be set when the current cursor is hovering over a "clickable" thing
        self._action_hover_cursor = QtCore.Qt.PointingHandCursor

    @property
    def thumbnail_role(self):
        """
        Get or set the index model data 'thumbnail' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        This role is used to retrieve the view item thumbnail; e.g. thumbnail = index.idata(thumbnail_role).
        """
        return self._thumbnail_role

    @thumbnail_role.setter
    def thumbnail_role(self, role):
        self._thumbnail_role = role

    @property
    def header_role(self):
        """
        Get or set the index model data 'title' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        This role is used to retrieve the view item title text; e.g. text = index.data(header_role).
        """
        return self._header_role

    @header_role.setter
    def header_role(self, role):
        self._header_role = role

    @property
    def subtitle_role(self):
        """
        Get or set the index model data 'subtitle' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        This role is used to retrieve the view item subtitle text; e.g. text = index.data(subtitle_role).
        """
        return self._subtitle_role

    @subtitle_role.setter
    def subtitle_role(self, role):
        self._subtitle_role = role

    @property
    def text_role(self):
        """
        Get or set the index model data 'text' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        This role is used to retrieve the view item main text; e.g. text = index.data(text_role).
        """
        return self._text_role

    @text_role.setter
    def text_role(self, role):
        self._text_role = role

    @property
    def short_text_role(self):
        """
        Get or set the index model data role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`). This
        role is used to retrieve the view item shortened text; e.g. text = index.data(short_text_role).
        The view item shortened text may be useful for thumbnail items that do not display well with
        longer text.
        """
        return self._short_text_role

    @short_text_role.setter
    def short_text_role(self, role):
        self._short_text_role = role

    @property
    def icon_role(self):
        """
        Get or set the index model data 'icon' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        This role is used to retrieve the view item icons; e.g. icons = index.data(icon_role). Icons are
        optional images that can be displayed on the item.
        """
        return self._icon_role

    @icon_role.setter
    def icon_role(self, role):
        self._icon_role = role

    @property
    def width_role(self):
        """
        Get or set the index model data item 'width' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        """
        return self._width_role

    @width_role.setter
    def width_role(self, role):
        self._width_role = role

    @property
    def height_role(self):
        """
        Get or set the index model data item 'height' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        """
        return self._height_role

    @height_role.setter
    def height_role(self, role):
        self._height_role = role

    @property
    def expand_role(self):
        """
        Get or set the index model data item 'expand' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        When this role is set, it will allow item rows to expand and collapse based on the text height.
        The index.data model does not need to do any additional work to enable this functionality, aside
        from providing a role for the delegate to use.
        """
        return self._expand_role

    @expand_role.setter
    def expand_role(self, role):
        self._expand_role = role

    @property
    def loading_role(self):
        """
        Get or set the index model data 'loading' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        The  data for this role will determine if a loading icon will be drawn for the view item.
        """
        return self._loading_role

    @loading_role.setter
    def loading_role(self, role):
        self._loading_role = role

    @property
    def separator_role(self):
        """
        Get or set the index model data 'separator' role (:class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`).
        The data for this role will determine if a separator will be drawn for the view item.
        """
        return self._separator_role

    @separator_role.setter
    def separator_role(self, role):
        self._separator_role = role

    @property
    def visible_lines(self):
        """
        Get or set the number of text lines the view item should display. This will omit any text that
        is beyond the number of visible lines.
        """
        return self._visible_lines

    @visible_lines.setter
    def visible_lines(self, lines):
        self._visible_lines = lines

    @property
    def document_style_sheet(self):
        """
        Get or set the default qss for the text document style sheet. This will affect the text style and layout of the item.
        """
        return self._document_style_sheet

    @document_style_sheet.setter
    def document_style_sheet(self, qss):
        self._document_style_sheet = qss

    @property
    def elide_text(self):
        """
        Get or set the flag indicating if the main text should be elided. If False, text will be wrapped.
        """
        return self._elide_text

    @elide_text.setter
    def elide_text(self, on):
        self._elide_text = on

    @property
    def elide_header(self):
        """
        Get or set the flag indicating if the header text should be elided. If False, text will be wrapped.
        """
        return self._elide_header

    @elide_header.setter
    def elide_header(self, on):
        self._elide_header = on

    @property
    def item_width(self):
        """
        Get or set the view item width. Set to None to ignore this property.
        """
        return self._item_width

    @item_width.setter
    def item_width(self, width):
        self._item_width = width

    @property
    def item_height(self):
        """
        Get or set the view item row height. If -1, this property is ignored.
        """
        return self._item_height

    @item_height.setter
    def item_height(self, height):
        self._item_height = height

        if (
            self._thumbnail_scale_value is not None
            and self._item_height is not None
            and self._item_height > 0
        ):
            # Scale the thumbnail width as the row height changes.
            self.thumbnail_width = self._item_height * self._thumbnail_scale_value

    @property
    def min_width(self):
        """
        Get or set the minimum width for an item.
        """
        return self._min_width

    @min_width.setter
    def min_width(self, width):
        self._min_width = width

    @property
    def min_height(self):
        """
        Get or set the minimum height for an item.
        """
        return self._min_height

    @min_height.setter
    def min_height(self, height):
        self._min_height = height

    @property
    def thumbnail_size(self):
        """
        Get or set the preferred size for the view item thumbnail. The value will be used to
        render the thumbnail, but the size of the thumbnail is not guaranteed to be the exact
        `thumbnail_size`.
        """
        return self._thumbnail_size

    @thumbnail_size.setter
    def thumbnail_size(self, size):
        self._thumbnail_size = size

    @property
    def thumbnail_width(self):
        """
        Get or set the preferred thumbnail width. Convenience property to set the width of the
        `thumbnail_size` property.
        """
        return self._thumbnail_size.width()

    @thumbnail_width.setter
    def thumbnail_width(self, width):
        self._thumbnail_size.setWidth(width)

    @property
    def thumbnail_height(self):
        """
        Get or set the preferred thumbnail height. Convenience property to set the height of the
        `thumbnail_size` property.
        """
        return self._thumbnail_size.height()

    @thumbnail_height.setter
    def thumbnail_height(self, height):
        self._thumbnail_size.setHeight(height)

    @property
    def pixmap_extent(self):
        """
        Get or set the extent used when converting :class:`sgtk.platform.qt.QtGui.QIcon` to a
        :class:`sgkt.platformqt.QtGui.QPixmap`.
        """
        return self._pixmap_extent

    @pixmap_extent.setter
    def pixmap_extent(self, extent):
        self._pixmap_extent = extent

    @property
    def icon_size(self):
        """
        Get or set the icon size for the view item action icons.
        """
        return self._icon_size

    @icon_size.setter
    def icon_size(self, size):
        self._icon_size = size

    @property
    def badge_height_pct(self):
        """
        Get or set the percentage value used to calculate the maximum badge icon height (e.g. badge
        icon is rendered over a rect, if that rect height is 100 and the `badge_height_pct` is 0.5,
        then the badge icon maximum height will be 50). Note that badge icons will only be scaled
        down to fit, not scaled up if the icon size is smaller than the max height.
        """
        return self._badge_height_pct

    @badge_height_pct.setter
    def badge_height_pct(self, pct):
        self._badge_height_pct = pct

    @property
    def action_item_margin(self):
        """
        Get or set the margin used for buttons.
        """
        return self._action_item_margin

    @action_item_margin.setter
    def action_item_margin(self, margin):
        self._action_item_margin = margin

    @property
    def button_padding(self):
        """
        Get or set the padding used for buttons.
        """
        return self._button_padding

    @button_padding.setter
    def button_padding(self, padding):
        self._button_padding = padding

    @property
    def text_document_margin(self):
        """
        Get or set the margin for the view item text. A :class:`sgtk.platform.qt.QtGui.QTextDocument` is used to
        render the view item text, this value will be used to set the QTextDocument margin property.
        """
        return self._text_document_margin

    @text_document_margin.setter
    def text_document_margin(self, margin):
        self._text_document_margin = margin

    @property
    def item_padding(self):
        """
        Get or set the view item padding. This value will add padding to the view item rect.
        """
        return self._item_padding

    @item_padding.setter
    def item_padding(self, padding):
        self._item_padding = None
        if isinstance(padding, self.Padding):
            self._item_padding = padding
        elif isinstance(padding, (int, float)):
            self._item_padding = self.Padding.new(padding)
        else:
            raise ValueError("Invalid padding value {}".format(padding))

    @property
    def thumbnail_padding(self):
        """
        Get or set the padding for the item thumbnail.
        """
        return self._thumbnail_padding

    @thumbnail_padding.setter
    def thumbnail_padding(self, padding):
        self._thumbnail_padding = None
        if isinstance(padding, self.Padding):
            self._thumbnail_padding = padding
        elif isinstance(padding, (int, float)):
            self._thumbnail_padding = self.Padding.new(padding)
        else:
            raise ValueError("Invalid padding value {}".format(padding))

    @property
    def text_padding(self):
        """
        Get or set the padding for the item text.
        """
        return self._text_padding

    @text_padding.setter
    def text_padding(self, padding):
        self._text_padding = None
        if isinstance(padding, self.Padding):
            self._text_padding = padding
        elif isinstance(padding, (int, float)):
            self._text_padding = self.Padding.new(padding)
        else:
            raise ValueError("Invalid padding value {}".format(padding))

    @property
    def text_rect_halign(self):
        """
        Get or set the text block horizontal alignment. This aligns the text block, not the text lines themselves (e.g. the
        block of text will be aligned within the available space, but the text lines will remain aligned left). Horizontal
        alignment will have no effect if there is a header and/or subtitle present (this causes the text block to expand
        to the full available width).
        """
        return self._text_rect_halign

    @text_rect_halign.setter
    def text_rect_halign(self, alignment):
        if alignment not in (self.LEFT, self.RIGHT, self.CENTER):
            raise ValueError(
                "Text horizontal alignment '{align}' not supported. Must be one of 'LEFT', 'RIGHT, 'CENTER'".format(
                    align=alignment
                )
            )
        self._text_rect_halign = alignment

    @property
    def text_rect_valign(self):
        """
        Get or set the text block vertical alignment.
        """
        return self._text_rect_valign

    @text_rect_valign.setter
    def text_rect_valign(self, alignment):
        if alignment not in (self.TOP, self.BOTTOM, self.CENTER):
            raise ValueError(
                "Text vertical alignment '{align}' not supported. Must be one of 'TOP', 'BOTTOM, 'CENTER'".format(
                    align=alignment
                )
            )
        self._text_rect_valign = alignment

    @property
    def font(self):
        """
        Get or set the font used to render the item text. If not specified, the QStyleOptionViewItem font value
        will be used.
        """
        return self._font

    @font.setter
    def font(self, value):
        self._font = value

    @property
    def background_pen(self):
        """
        Get or set the :class:`sgtk.platform.qt.QGui.QPen` pen used to draw the view item background.
        Setting this value will add a border around the view item.
        """
        return self._background_pen

    @background_pen.setter
    def background_pen(self, pen):
        self._background_pen = pen

    @property
    def loading_pen(self):
        """
        Get or set the :class:`sgtk.platform.qt.QtGui.QPen` pen used to draw the item loading indicator.
        """
        return self._loading_pen

    @loading_pen.setter
    def loading_pen(self, pen):
        self._loading_pen = pen

    @property
    def loading_brush(self):
        """
        Get or set the :class:`sgtk.platform.qt.QtGui.QBrush` brush used to paint the background of the item
        loading rect.
        """
        return self._loading_brush

    @loading_brush.setter
    def loading_brush(self, brush):
        self._loading_brush = brush

    @property
    def selection_brush(self):
        """
        Get or set the :class:`sgtk.platform.qt.QGui.QBrush` used to draw the view item selection.
        """
        return self._selection_brush

    @selection_brush.setter
    def selection_brush(self, brush):
        self._selection_brush = brush

    @property
    def separator_brush(self):
        """
        Get or set the :class:`sgtk.platform.qt.QGui.QBrush` used to draw the view item separator.
        """
        return self._separator_brush

    @separator_brush.setter
    def separator_brush(self, brush):
        self._separator_brush = brush

    @property
    def show_hover_selection(self):
        """
        Get or set the flag indicating to draw selection on hover or not. The default is set to True.
        """
        return self._show_hover_selection

    @show_hover_selection.setter
    def show_hover_selection(self, show):
        self._show_hover_selection = show

    @property
    def show_text_tooltip(self):
        """
        Get or set the flag indicating to show a tooltip if the item text has been elided.
        """
        return self._show_text_tooltip

    @property
    def override_item_tooltip(self):
        """
        Get or set the flag indicating to override the tooltip set on the QStandardItem object. Note that
        this will only affect indexes that have an associated QStandardItem (e.g. the index model derives
        from the QStandardItemModel class).
        """
        return self._override_item_tooltip

    @override_item_tooltip.setter
    def override_item_tooltip(self, override):
        self._override_item_tooltip = override

    @show_text_tooltip.setter
    def show_text_tooltip(self, show):
        self._show_text_tooltip = show

    @property
    def action_hover_cursor(self):
        """
        Get or set the cursor :class:`sgtk.platform.qt.QtGui.QCursor` for when an action button is
        hovered over.
        """
        return self._action_hover_cursor

    @action_hover_cursor.setter
    def action_hover_cursor(self, cursor):
        self._action_hover_cursor = cursor

    @staticmethod
    def get_option_background_brush(option):
        """
        Return the background brush for the QStyleOptionviewItem object.

        NOTE: This method should be used to retrieve the QStyleOptionViewItem's
        backgroundBrush property. For different version of Qt, the backgroundBrush
        property may not exist.

        :param option: The option to get the background brush from.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`

        :return: The option's background brush object.
        :rtype: :class:`sgtk.platform.qt.QtGui.QBrush`
        """

        try:
            return option.backgroundBrush
        except AttributeError:
            return option.palette.brush(QtGui.QPalette.Background)

    @staticmethod
    def is_selected(option):
        """
        Return True if the item is selected.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`

        :return: True if the item is selected, else False.
        :rtype: bool
        """

        return option.state & QtGui.QStyle.State_Selected

    @staticmethod
    def get_value(index, role, default_value=None):
        """
        Return the index.data for the given role. If the data returned is
        a function, return the value of the executing the function.

        :param role: The item data role
        :type role: :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`

        :return: The value for the index and role. If the value found is None,
                 the default_value will be returned.
        """

        if role is None:
            return None

        data = index.data(role)
        if callable(data):
            # If the data itself is a function, execute the function to get the data value.
            data = data()

        if data is None:
            return default_value

        return data

    @staticmethod
    def get_display_values_list(index, role, flat=False, join_char=None):
        """
        Return a list of display string values. Each return item in the list
        represents a text line.

        :param role: The item data role
        :type role: :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`
        :param flat: If True, the value returned will be the list of values joined
                     by the 'join_char' (default join char is "")
        :type flat: bool
        :param join_char: Used to join the list of values to return a single value, when
                          `flat` is True.
        :type join_char: str

        :return: A list of display values. An empty list is returned if no data
                is found, or was unable to parse the data for the index's role.
        :rtype: list<str>
        """

        data = ViewItemDelegate.get_value(index, role)
        values_list = None

        if data is None:
            values_list = []

        elif isinstance(data, six.string_types):
            values_list = [data]

        elif isinstance(data, (list, tuple)):
            if (
                len(data) == 2
                and isinstance(data[0], six.string_types)
                and isinstance(data[1], dict)
            ):
                # Special SG string formatting data
                values_list = [utils.convert_token_string(data[0], data[1])]
            else:
                values_list = list(data)

        elif isinstance(data, dict):
            values_list = []
            for key, value in data.items():
                if isinstance(key, six.string_types) and isinstance(
                    value, six.string_types
                ):
                    values_list.append("<b>%s</b>:  %s" % (key, value))
            return values_list

        else:
            # Ensure items in values_list are strings
            values_list = [str(data)]

        if flat:
            # Return the values listed flattened
            if join_char is None:
                join_char = ""
            return join_char.join(values_list)

        # Return the values list
        return values_list

    @staticmethod
    def split_html_lines(html_text):
        """
        Convenience method to split html text by line break tags.
        """

        return re.split(r"<br\s*/?>", html_text)

    ######################################################################################################
    # Public methods

    def is_hover(self, option):
        """
        Return True if the mouse is over the item. This will always return
        False if the option does not have a widget or the option's widget
        does not have mouse tracking enabeld.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`

        :return: True if the mouse is over the item, else False.
        :rtype: bool
        """

        return self.has_mouse_tracking(option) and (
            option.state & QtGui.QStyle.State_MouseOver
        )

    def has_mouse_tracking(self, option):
        """
        Return True if the item's option widget has mouse tracking enabled.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`

        :return: True if the item has mouse tracking enabled.
        :rtype: bool
        """

        widget = self.get_option_widget(option)
        return widget and widget.hasMouseTracking()

    def get_cursor_pos(self, option):
        """
        Return the mouse cursor position relative to the item's widget. This
        will always return False if the option's widget does not have
        mouse tracking enabled.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`

        :return: The cursor position relative to the option widget.
        :rtype: :class:`sgkt.platform.qt.QtCore.QPoint`
        """

        if self.has_mouse_tracking(option):
            widget = self.get_option_widget(option)
            return widget.mapFromGlobal(QtGui.QCursor.pos())

        return None

    def get_option_widget(self, option):
        """
        Return the widget for the QStyleOptionviewItem object.

        NOTE: This method should be used to retrieve the QStyleOptionViewItem's widget property.
        For different version of Qt, the widget is stored in different properties.

        :param option: The option to get the widget from.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`

        :return: The option's widget object.
        :rtype: :class:`sgtk.platform.qt.QtGui.QWidget`
        """

        try:
            widget = option.widget
        except AttributeError:
            widget = None

        if widget is None:
            try:
                widget = option.styleObject
            except AttributeError:
                # Fall back to the delegate's view
                widget = self._view

        return widget

    def add_actions(self, actions, position=FLOAT_BOTTOM_RIGHT):
        """
        Add actions that will be made available to show for each item. This method should be used to
        add actions to the `_actions` field instead of editing it directly.

        :param actions: The actions to add.
        :type actions: list<dict>, where each dict represents the action. The dict will be passed to
                       the ViewItemAction constructor to create a ViewItemAction object.
        :param position: The position to display the actions.
        :type position: POSITION enum, defaults to float on the bottom right of the item rect.
        """

        for action in actions:
            item_action = ViewItemAction(action)
            self._actions.setdefault(position, []).append(item_action)

    def add_action(self, action, position=FLOAT_BOTTOM_RIGHT):
        """
        Convenience method to add an action. See `add_actions`.

        :param actions: The actions to add.
        :type actions: list<dict>, where each dict represents the action. The dict will be passed to
                       the ViewItemAction constructor to create a ViewItemAction object.
        :param position: The position to display the actions.
        :type position: POSITION enum, defaults to float on the bottom right of the item rect.
        """

        return self.add_actions([action], position)

    def remove_actions(self, positions=None):
        """
        Remove the actions at the specified position. If positions are not specified, remove
        all actions.

        :param positions: The list of positions to remove actions from.
        :type positions: list<POSITION>, where POSITION is one of the POSITIONS enum.
        """

        if not positions:
            self._actions.clear()

        else:
            for position in positions:
                self._actions[position].clear()

    def scale_thumbnail_to_item_height(self, scale_value):
        """
        If scale_value is not None, the thumbnail width will scale with the row height by a factor
        of `scale_value` (e.g. thumbnail_width = item_height * scale_value). This is convenient when
        the item size is adjusted dynmaically (e.g. using a slider) and this will scale up and down
        the thumbnail with the item size.

        :param scale_value: The value to scale the thumbnail by.
        :type scale_value: float
        """

        self._thumbnail_scale_value = scale_value

    def get_displayed_text(self, index):
        """
        Return the text that is displayed for the item. The text will be plain (not rich HTML).
        This may be useful for filtering items displayed by this delegate, since the model data
        may be formatted by the delegate before being displayed.

        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        # Create dummy view options and rect, in order to get the text.
        dummy_option = QtGui.QStyleOptionViewItem()
        dummy_rect = QtCore.QRect(0, 0, -1, -1)
        doc, _ = self._get_text_document(dummy_option, index, dummy_rect, clip=False)

        return doc.toPlainText()

    ###############################################################################################
    # Override :class:`sgtk.platform.qt.QtGui.QStyledItemDelegate` methods

    def initStyleOption(self, option, index):
        """
        Overrides :class:`sgtk.platform.qt.QtGui.QStyledItemDelegate` method.

        Initialize the option used for rendering the item. This should be called before using
        the option (e.g. sizeHint, paint, etc.).

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        # Adjust the option rect to account for padding around the view item content.
        option.rect.adjust(
            self.item_padding.left,
            self.item_padding.top,
            -self.item_padding.right,
            -self.item_padding.bottom,
        )

        super(ViewItemDelegate, self).initStyleOption(option, index)

    def createEditor(self, parent, option, index):
        """
        Overrides :class:`sgtk.platform.qt.QtGui.QStyledItemDelegate` method.

        This default implementation does not provide an editor.

        :param parent: The editor's parent widget.
        :type parent: :class:`sgtk.platform.qt.QtGui.QWidget`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :return: The editor widget for the item.
        :rtype: :class:`sgtk.platform.qt.QtGui.QWidget`
        """

        return None

    def editorEvent(self, event, model, option, index):
        """
        Overrides :class:`sgtk.platform.qt.QtGui.QStyledItemDelegate` method.

        Listens for left mouse button press events to check if a view item action
        should be triggered.

        If mouse tracking has been enabled on the option's widget, this method
        will listens and act on mouse move events, even if there is no editor
        set up for the item.

        :param event: The event that triggered the editing. Mouse events are sent to
                      this method even if they do not start editing the item.
        :type event: :class:`sgtk.platform.qt.QtCore.QEvent`
        :param model: The model of the item.
        :type model: :class:`sgtk.platform.qt.QtCore.QAbstractItemModel`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :return: True if the event was handled, else False (it was ignored).
        :rtype: bool
        """

        # Initialize the view option
        view_option = QtGui.QStyleOptionViewItem(option)
        self.initStyleOption(view_option, index)

        if (
            event.type() == QtCore.QEvent.MouseButtonPress
            and event.button() == QtCore.Qt.LeftButton
        ):
            action = self._action_at(view_option, index, event.pos())
            if action and action.is_clickable(self.parent(), index):

                if action.callback:
                    # Trigger the action callback function if the action defines one
                    action.callback(self.parent(), index, event.pos())

                elif action.type in ViewItemAction.checkable_types():
                    # The default behaviour for checkable actions is to set the index check state role data;
                    # however, this only works if there is a single checkable action for the index, or else
                    # each checkable action will modify the same data role property. For multiple checkable
                    # actions for an index (item), callbacks for each action need to be defined.
                    check_state_role = action.check_state_role
                    if index.data(check_state_role) == QtCore.Qt.Checked:
                        new_check_state = QtCore.Qt.Unchecked
                    else:
                        new_check_state = QtCore.Qt.Checked
                    index.model().setData(index, new_check_state, check_state_role)

                else:
                    assert False, "Action is clickable but has no callback to execute"

                # Return True to incate the event has been handled.
                return True

        elif event.type() == QtCore.QEvent.MouseMove:
            widget = self.get_option_widget(view_option)

            if self.action_hover_cursor and widget:
                action = self._action_at(view_option, index, event.pos())
                if action and action.is_clickable(self.parent(), index):
                    # Set the cursor to indicate the action is clickable
                    widget.setCursor(self.action_hover_cursor)
                else:
                    widget.unsetCursor()

            # Emit a data changed signal for the index to paint according to the mouse move
            # event (e.g. hover selection).
            # TODO: leverage the 'roles' parameter to emit only the relevant data roles
            # to consider, for a more efficient update. Currently there are some issues using
            # this parameter due to mismatch method signatures between versions.
            model.dataChanged.emit(index, index)

            # Fall through to allow the base implementation to perform any other mouse move event handling

        return super(ViewItemDelegate, self).editorEvent(
            event, model, view_option, index
        )

    def sizeHint(self, option, index):
        """
        Overrides :class:`sgtk.platform.qt.QtGui.QStyledItemDelegate` method.

        Returns the size hint for the view item.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        if not index.isValid():
            return QtCore.QSize()

        # Initialize the view option
        view_option = QtGui.QStyleOptionViewItem(option)
        self.initStyleOption(view_option, index)

        # Default width and height to -1, indicating no size hint and that the item width/height
        # should expand to the full available space.
        width = -1
        height = -1

        # Calculate the width of the item.
        if self.item_width is not None:
            # The width is fixed for all items.
            width = self.item_width
        else:
            # Set the width to the value defined by the index data.
            width = self.get_value(index, self.width_role)

        if width is None:
            # Default to the option rect width if not set
            width = option.rect.width()

        # For valid width values, ensure it is the minumum width and add padding.
        if width >= 0:
            width = max(width, self.thumbnail_width, self.min_width)

        # Calculate the height of the item.
        index_height = self.get_value(index, self.height_role)
        if (
            self.item_height is None
            or self.item_height < 0
            or index_height is not None
            or self.get_value(index, self.expand_role)
        ):
            if index_height is None or index_height < 0:
                # The item height expands to the height of the text. NOTE the view that this delegate is
                # set to must not have uniform items set for this to resize properly.

                text_rect = self._get_text_rect(view_option, index)
                text_doc, _ = self._get_text_document(
                    view_option, index, text_rect, clip=False
                )
                text_height = text_doc.size().height()
                height_for_visible_lines = self._get_visible_lines_height(option)
                height_for_actions = self._get_actions_maximum_height(option, index)
                height = max(text_height, height_for_visible_lines, height_for_actions)
            else:
                # Set the height the value defined by the index data.
                height = index_height
        else:
            # The height is fixed for all items.
            height = self.item_height

        # Ensure height is not None, set it to -1 to indicate no size hint for height
        if height is None:
            height = -1

        # For valid height values, ensure it is the minumum height and add padding.
        if height >= 0:
            height = max(height, self.min_height)
            height += self.item_padding.top + self.item_padding.bottom
            height += self.text_padding.top + self.text_padding.bottom

        return QtCore.QSize(width, height)

    def paint(self, painter, option, index):
        """
        Overrides :class:`sgtk.platform.qt.QtGui.QStyledItemDelegate` method.

        The main paint method that draws each item in the view. Override specific draw
        methods to customize the rendered item, if needed.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        if not index.isValid():
            return

        # Initialize the view option
        view_option = QtGui.QStyleOptionViewItem(option)
        self.initStyleOption(view_option, index)
        # The styleObject propety is cleared by initStyleOption, but for Qt versions < 5.12 the
        # styleObject is required since that is where the option's widget is stored (instead of
        # option.widget property as in Qt >= 5.12), so we will just reset the styleObject back
        # to the incoming options' styleObject value.
        try:
            view_option.styleObject = option.styleObject
        except AttributeError:
            # Fall back to use the view as the style object for Qt versions where QStyleOption
            # does not have a widget or styleObject property.
            view_option.styleObject = self._view

        # Check if the index should be expanded or collapsed, and update the index
        # model data to render the correct row height for the index.
        self._update_index_expand_state(view_option, index)

        painter.save()
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing
        )

        self._draw_background(painter, view_option)
        thumbnail_rect = self._draw_thumbnail(painter, view_option, index)
        self._draw_text(painter, view_option, index)
        self._draw_actions(painter, view_option, index)
        self._draw_separator(painter, view_option, index)

        if self.is_selected(view_option) or (
            self.show_hover_selection and self.is_hover(view_option)
        ):
            self._draw_selection(painter, view_option)

        self._draw_icon_badges(painter, view_option, thumbnail_rect, index)
        self._draw_loading(painter, view_option, index)

        painter.restore()

        if DEBUG_PAINT:
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.magenta))
            painter.drawRect(option.rect)
            painter.setPen(QtGui.QPen(QtCore.Qt.cyan))
            painter.drawRect(view_option.rect)
            painter.restore()

    ######################################################################################################
    # Draw Methods
    # Override any of these draw methods to customize how that particular aspect of the item is rendered.

    def _draw_background(self, painter, option):
        """
        Draw the view item background. This default implementation will fill the option rect using the
        option background brush. Modify the option background brush by returning a
        :class:`sgtk.platform.qt.QtGui.QBrush` for index.data role `sgtk.platform.qt.QtCore.Qt.BackgroundRole`.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        """

        painter.save()
        painter.setBrush(QtGui.QBrush(self.get_option_background_brush(option)))
        painter.setPen(self.background_pen)
        painter.drawRoundedRect(option.rect, self._item_x_radius, self._item_y_radius)
        painter.restore()

    def _draw_loading(self, painter, option, index):
        """
        Draw the animated loading indicator. This default implementation will render an arc rotating
        in a circle for as long as the item data indicates that the item is in a loading state.

        The formula used to render the spinning loader is borrowed from the :class:`SpinnerWidget`.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        rect = self._get_loading_rect(option, index)
        if not rect.isValid():
            return

        if self._loading_brush and self._loading_brush != QtCore.Qt.NoBrush:
            # Paint the background while loading.
            painter.save()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(self._loading_brush)
            painter.drawRoundedRect(
                option.rect, self._item_x_radius, self._item_y_radius
            )
            painter.restore()

        # Calculate spin angle as a function of time so that all spinners appear in sync
        # This uses the same function as the SpinnerWidget
        s = time()
        p = s % self._seconds_per_spin
        start_angle = int((360 * p) / self._seconds_per_spin)

        if self.loading_pen:
            pen = self.loading_pen
        else:
            widget = self.get_option_widget(option)
            color = (
                option.palette.color(widget.foregroundRole())
                if widget
                else option.palette.text().color()
            )
            pen = QtGui.QPen(color)
            pen.setWidth(2)

        painter.save()
        painter.setPen(pen)
        painter.drawArc(rect, -start_angle * 16, self._spin_arc_len * 16)
        painter.restore()

        if DEBUG_PAINT:
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.magenta))
            painter.drawRect(rect)
            painter.restore()

        # Emit a data changed signal for the index to continue painting the animation until
        # the item has finished loading.
        # TODO: leverage the 'roles' parameter to emit only the relevant data roles
        # to consider, for a more efficient update. Currently there are some issues using
        # this parameter due to mismatch method signatures between versions.
        index.model().dataChanged.emit(index, index)

    def _draw_separator(self, painter, option, index):
        """
        Draw a line to separate this view item from the next. This default implementation will
        render a line from the bottom left corner to the bottom right, in the same color used
        by the option palette foreground, if available, or the option widget text color.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        if not self.separator_role:
            return

        separator = self.get_value(index, self.separator_role)
        if not separator:
            return

        # TODO support decorations in the separator (e.g. icon or text with the horizontal line)
        position = self.POSITIONS[self.BOTTOM]
        if isinstance(separator, dict):
            position = separator.get("position", position)

        if self.separator_brush == QtCore.Qt.NoBrush:
            widget = self.get_option_widget(option)
            color = (
                option.palette.color(widget.foregroundRole())
                if widget
                else option.palette.text().color()
            )
            pen = QtGui.QPen(color)
            pen.setWidthF(0.5)

        else:
            pen = QtGui.QPen(self.separator_brush.color())

        if position == self.POSITIONS[self.TOP]:
            start = option.rect.topLeft()
            end = option.rect.topRight()
        else:
            # Draw the line from the bottom left corner to bottom right
            start = option.rect.bottomLeft()
            end = option.rect.bottomRight()

        painter.save()
        painter.setBrush(self._separator_brush)
        painter.setPen(pen)
        painter.drawLine(start, end)
        painter.restore()

    def _draw_selection(self, painter, option):
        """
        Draw the view item selection. This default implementation will draw a border around
        the item rect and a translucent background, in the color the the option palette
        highlight color.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        """

        if self.selection_brush == QtCore.Qt.NoBrush:
            brush = QtCore.Qt.NoBrush
            pen = QtCore.Qt.NoPen
        elif self.selection_brush:
            brush = self.selection_brush
            pen = QtGui.QPen(QtCore.Qt.NoPen)
            pen.setWidth(2)
        else:
            pen = QtGui.QPen(option.palette.highlight().color())
            pen.setWidth(2)
            fill_color = pen.color()
            fill_color.setAlpha(30)
            brush = QtGui.QBrush(fill_color)

        painter.save()
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(option.rect, self._item_x_radius, self._item_y_radius)
        painter.restore()

    def _draw_thumbnail(self, painter, option, index):
        """
        Draw the view item thumbnail. This default implementation will scale the thumbnail width
        and height down to the thumbnail rect size, if larger, keeping the aspect ratio. The
        thumbnail will also be centered within the calculated thumbnail rect.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        thumbnail = self._get_thumbnail(index)

        if thumbnail:
            available_rect = self._get_thumbnail_rect(option, index, thumbnail)
            available_size = available_rect.size()

            # Scale the thumbnail to the available space
            if thumbnail.height() > available_size.height():
                thumbnail = thumbnail.scaledToHeight(available_size.height())

            if thumbnail.width() > available_size.width():
                thumbnail = thumbnail.scaledToWidth(available_size.width())

            # Adjust the available rect to the size of the thumbnail and center it
            if thumbnail.size() != available_size:
                thumbnail_rect = QtCore.QRect(available_rect)
                thumbnail_rect.setSize(thumbnail.size())

                # Calculate horizontal offset
                if self.LEFT in self.thumbnail_position:
                    dx = 0
                elif self.RIGHT in self.thumbnail_position:
                    dx = available_rect.width() - thumbnail.size().width()
                else:
                    # Default to center horizontally
                    dx = (available_rect.width() - thumbnail.size().width()) / 2

                # Calculate vertical offset
                if self.TOP in self.thumbnail_position:
                    dy = 0
                elif self.BOTTOM in self.thumbnail_position:
                    dy = available_rect.height() - thumbnail.size().height()
                else:
                    # Default to center vertically
                    dy = (available_rect.height() - thumbnail.size().height()) / 2

                thumbnail_top_left = thumbnail_rect.topLeft()
                thumbnail_rect.moveTo(
                    thumbnail_top_left.x() + dx, thumbnail_top_left.y() + dy
                )

            else:
                thumbnail_rect = available_rect

            # Create a brush with the thumbnail as a texture, so that the painter can draw the pixmap
            # as a rounded rect.
            pixmap = QtGui.QBrush(thumbnail)

            # Draw the pixmap
            painter.save()
            painter.setPen(self._thumbnail_pen)
            painter.setBrush(pixmap)
            painter.translate(thumbnail_rect.topLeft())
            painter.drawRoundedRect(
                0,
                0,
                thumbnail_rect.width(),
                thumbnail_rect.height(),
                self._thumbnail_x_radius,
                self._thumbnail_y_radius,
            )
            painter.restore()

            if DEBUG_PAINT:
                painter.save()
                painter.translate(thumbnail_rect.topLeft())
                painter.setPen(QtGui.QPen(QtCore.Qt.yellow))
                painter.drawRoundedRect(
                    0,
                    0,
                    thumbnail_rect.width(),
                    thumbnail_rect.height(),
                    self._thumbnail_x_radius,
                    self._thumbnail_y_radius,
                )
                painter.restore()
        else:
            available_rect = QtCore.QRect()
            thumbnail_rect = QtCore.QRect()

        return thumbnail_rect

    def _draw_icon_badges(self, painter, option, bounding_rect, index):
        """
        Draw the badges for this index item. This method supports drawing up to four
        badges, one is each corner of the given `bounding_rect`.

        The index.data describes the badges to draw; the data is expected to be
        a single :class:`sgtk.platform.qt.QtGui.QPixmap` or a dict with possible keys-values:
            {
                "[float-]top-left": :class:`sgtk.platform.qt.QtGui.QPixmap`,
                "[float-]top-right": :class:`sgtk.platform.qt.QtGui.QPixmap`,
                "[float-]bottom-left": :class:`sgtk.platform.qt.QtGui.QPixmap`,
                "[float-]bottom-right": :class:`sgtk.platform.qt.QtGui.QPixmap`,
            }
        Floating and non-floating position keys accepted; however all icons will be drawn
        in a "floating" orientation.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param bounding_rect: The rect that the badge icons will be overlayed.
        :type bounding_rect: :class:`sgtk.platform.qt.QtCore.QRect`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        # Default to the option rect if the giving bounding rect is invalid
        if not bounding_rect.isValid():
            bounding_rect = option.rect

        badge_data = self.get_value(index, self.icon_role)
        if not badge_data:
            return

        if isinstance(badge_data, QtGui.QPixmap):
            # Default to bottom right if only a pixmap given.
            badge_data = {"bottom-right": badge_data}

        if isinstance(badge_data, dict):
            for position, pixmap_data in badge_data.items():
                if not pixmap_data:
                    continue

                # The pixmap to display for the icon badge
                pixmap = None
                # Inset will display the badge inside the bounding rect, otherwise the badge
                # will be display centered over the corner corresponding to the badge position.
                inset = True
                if isinstance(pixmap_data, dict):
                    pixmap = pixmap_data.get("pixmap", None)
                    inset = pixmap_data.get("inset", True)
                else:
                    pixmap = pixmap_data

                if isinstance(pixmap, QtGui.QIcon):
                    pixmap = self._convert_icon_to_pixmap(pixmap)
                elif isinstance(pixmap, six.string_types):
                    pixmap = QtGui.QPixmap(pixmap)

                if not pixmap or not isinstance(pixmap, QtGui.QPixmap):
                    # Skip, invalid pixmap data.
                    continue

                if (
                    self.badge_height_pct
                    and pixmap.height() > option.rect.height() * self.badge_height_pct
                ):
                    # Scale the pixmap to fit neatly into a corner
                    pixmap = pixmap.scaledToHeight(
                        option.rect.height() * self.badge_height_pct
                    )

                pixmap_size = pixmap.size()

                if position in (
                    self.POSITIONS[self.TOP_LEFT],
                    self.POSITIONS[self.FLOAT_TOP_LEFT],
                ):
                    if inset:
                        point = QtCore.QPoint(
                            bounding_rect.left() + self.button_padding,
                            bounding_rect.top() + self.button_padding,
                        )
                    else:
                        point = bounding_rect.topLeft()
                        point += QtCore.QPoint(
                            -pixmap_size.width() / 2.0,
                            -pixmap_size.height() / 2.0,
                        )

                elif position in (
                    self.POSITIONS[self.TOP_RIGHT],
                    self.POSITIONS[self.FLOAT_TOP_RIGHT],
                ):
                    if inset:
                        point = QtCore.QPoint(
                            bounding_rect.right()
                            - self.button_padding
                            - pixmap_size.width(),
                            bounding_rect.top() + self.button_padding,
                        )
                    else:
                        point = bounding_rect.topRight()
                        point += QtCore.QPoint(
                            -pixmap_size.width() / 2.0,
                            -pixmap_size.height() / 2.0,
                        )
                elif position in (
                    self.POSITIONS[self.BOTTOM_LEFT],
                    self.POSITIONS[self.FLOAT_BOTTOM_LEFT],
                ):
                    if inset:
                        point = QtCore.QPoint(
                            bounding_rect.left() + self.button_padding,
                            bounding_rect.bottom()
                            - self.button_padding
                            - pixmap_size.height(),
                        )
                    else:
                        point = bounding_rect.bottomLeft()
                        point += QtCore.QPoint(
                            -pixmap_size.width() / 2.0,
                            -pixmap_size.height() / 2.0,
                        )
                else:
                    # Default to bottom right corner.
                    if inset:
                        point = QtCore.QPoint(
                            bounding_rect.right()
                            - self.button_padding
                            - pixmap_size.height(),
                            bounding_rect.bottom()
                            - self.button_padding
                            - pixmap_size.height(),
                        )
                    else:
                        point = bounding_rect.bottomRight()
                        point += QtCore.QPoint(
                            -pixmap_size.width() / 2.0,
                            -pixmap_size.height() / 2.0,
                        )

                badge_rect = QtCore.QRect(point, pixmap.size())
                painter.drawPixmap(badge_rect, pixmap)

    def _draw_text(self, painter, option, index):
        """
        Draw the view item text. This will get the whole text document and use the QTextDocument
        method `drawContents` to render the text, in order to handle HTML/rich text.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        rect = self._get_text_rect(option, index)
        if not rect.isValid():
            return

        doc, elided = self._get_text_document(option, index, rect)

        # Vertical text alignment
        text_height = doc.size().height()
        available_height = rect.height()
        dy = 0
        if text_height < available_height:
            if self.text_rect_valign == self.CENTER:
                dy = (available_height - text_height) / 2

            elif self.text_rect_valign == self.BOTTOM:
                dy = available_height - text_height

        # Horizontal text alignment
        text_width = doc.idealWidth()
        available_width = rect.width()
        dx = 0
        if text_width < available_width:
            if self.text_rect_halign == self.CENTER:
                dx = (available_width - text_width) / 2

            elif self.text_rect_halign == self.RIGHT:
                dx = available_width - text_width

        # Get the point to translate the painter, before drawing the text.
        origin = QtCore.QPoint(rect.left() + dx, rect.top() + dy)

        painter.save()
        painter.translate(origin)
        doc.drawContents(painter)
        painter.restore()

        if DEBUG_PAINT:
            painter.save()
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtGui.QPen(QtCore.Qt.red))
            painter.drawRect(rect)
            painter.restore()

        # Draw the text tooltip. Check if text is elided here, since we've arleady did
        # some work to check for text eliding.
        if not elided:
            # FIXME we need to specifically check the header if it was elided, as this does not
            # get caught in the main `_get_text_document` method.
            _, elided = self._get_header_text(index, option, rect, return_elided=True)

        self._draw_text_tooltip(option, rect, index, elided)

    def _draw_actions(self, painter, view_option, index):
        """
        Paint the actions for the view item. Actions are rendered using the option
        widget's QStyle (or defaults to the application QStyle) as passing in QStyleOptionButton
        options to specifiy how the action button should be displayed.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        # Get the list of available actions for this item, and their corresponding boudning rect.
        actions_and_rects = self._get_action_and_rects(view_option, index)

        for action, rect in actions_and_rects:
            if not action or not rect.isValid():
                continue

            painter.save()
            painter.setFont(view_option.font)

            if (
                action.type == ViewItemAction.TYPE_PUSH_BUTTON
                or action.type == ViewItemAction.TYPE_ICON
            ):
                self._draw_action_push_button(painter, view_option, index, action, rect)

            elif action.type == ViewItemAction.TYPE_RADIO_BUTTON:
                self._draw_action_radio_button(
                    painter, view_option, index, action, rect
                )

            elif action.type == ViewItemAction.TYPE_CHECK_BOX:
                self._draw_action_check_box(painter, view_option, index, action, rect)

            elif action.type == ViewItemAction.TYPE_PROGRESS_BAR:
                self._draw_action_progress_bar(
                    painter, view_option, index, action, rect
                )

            painter.restore()

            if DEBUG_PAINT:
                painter.save()
                painter.setPen(QtGui.QPen(QtCore.Qt.cyan))
                painter.drawRect(rect)
                painter.restore()

    def _draw_action_push_button(self, painter, view_option, index, action, rect):
        """
        Draw the action as a push button.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item to render.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param action: The action to draw the push button for
        :type action: ViewItemAction
        :param rect: The action's bounding rect
        :type rect: QRect
        """

        index_data = action.get_data(self.parent(), index)
        if not index_data.get("visible", True) or index_data.get("placeholder", False):
            # Do not draw actions that are not visible or are placeholders
            return

        widget = self.get_option_widget(view_option)
        button_option = self._get_action_button_option(
            view_option, widget, action, rect, index_data
        )

        self._draw_push_button(painter, button_option, widget)

        if button_option.state & QtGui.QStyle.State_MouseOver:
            tooltip = index_data.get("tooltip", action.tooltip)
            if tooltip:
                QtCore.QTimer.singleShot(
                    500,
                    lambda o=view_option, r=rect, t=tooltip: self._draw_tooltip(
                        o, r, t
                    ),
                )

    def _draw_action_radio_button(self, painter, view_option, index, action, rect):
        """
        Draw the action as a radio button.

        To draw a "checked" radio button, the state must include the flag QtGui.QStyle.State_On.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item to render.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param action: The action to draw the push button for
        :type action: ViewItemAction
        :param rect: The action's bounding rect
        :type rect: QRect
        """

        index_data = action.get_data(self.parent(), index)
        if not index_data.get("visible", True) or index_data.get("placeholder", False):
            # Do not draw actions that are not visible or are placeholders
            return

        widget = self.get_option_widget(view_option)
        button_option = self._get_action_button_option(
            view_option, widget, action, rect, index_data
        )
        style = widget.style() if widget else QtGui.QApplication.style()

        style.proxy().drawControl(QtGui.QStyle.CE_RadioButton, button_option, painter)

        if button_option.state & QtGui.QStyle.State_MouseOver:
            tooltip = index_data.get("tooltip", action.tooltip)
            if tooltip:
                QtCore.QTimer.singleShot(
                    500,
                    lambda o=view_option, r=rect, t=tooltip: self._draw_tooltip(
                        o, r, t
                    ),
                )

    def _draw_action_check_box(self, painter, view_option, index, action, rect):
        """
        Draw the action as a check box.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item to render.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param action: The action to draw the push button for
        :type action: ViewItemAction
        :param rect: The action's bounding rect
        :type rect: QRect
        """

        index_data = action.get_data(self.parent(), index)
        if not index_data.get("visible", True) or index_data.get("placeholder", False):
            # Do not draw actions that are not visible or are placeholders
            return

        widget = self.get_option_widget(view_option)
        button_option = self._get_action_button_option(
            view_option, widget, action, rect, index_data
        )

        if button_option.icon:
            # Checkbox is displayed using an icon, draw it as a flat button
            self._draw_push_button(painter, button_option, widget)
        else:
            style = widget.style() if widget else QtGui.QApplication.style()
            style.proxy().drawControl(QtGui.QStyle.CE_CheckBox, button_option, painter)

        if button_option.state & QtGui.QStyle.State_MouseOver:
            tooltip = index_data.get("tooltip", action.tooltip)
            if tooltip:
                QtCore.QTimer.singleShot(
                    500,
                    lambda o=view_option, r=rect, t=tooltip: self._draw_tooltip(
                        o, r, t
                    ),
                )

    def _draw_action_progress_bar(self, painter, view_option, index, action, rect):
        """
        Draw the action as a progress bar.

        :param painter: the object used for painting.
        :type painter: :class:`sgkt.platform.qt.QtGui.QPainter`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item to render.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param action: The action to draw the push button for
        :type action: ViewItemAction
        :param rect: The action's bounding rect
        :type rect: QRect
        """

        index_data = action.get_data(self.parent(), index)
        if not index_data.get("visible", True) or index_data.get("placeholder", False):
            # Do not draw actions that are not visible or are placeholders
            return

        widget = self.get_option_widget(view_option)
        progress_bar_option = self._get_action_progress_bar_option(
            view_option, widget, action, rect, index_data
        )
        style = widget.style() if widget else QtGui.QApplication.style()

        style.proxy().drawControl(
            QtGui.QStyle.CE_ProgressBar, progress_bar_option, painter
        )

        if progress_bar_option.state & QtGui.QStyle.State_MouseOver:
            tooltip = index_data.get("tooltip", action.tooltip)
            if tooltip:
                QtCore.QTimer.singleShot(
                    500,
                    lambda o=view_option, r=rect, t=tooltip: self._draw_tooltip(
                        o, r, t
                    ),
                )

    def _draw_push_button(self, painter, button_option, widget):
        """
        Draw a push button.

        Ideally calling QStyle.drawControl method with QStyle.CE_PushButton could render the push button, but
        there are issues with certain styles, so the QCommonStyle drawControl method is reimplemented with
        some special handling.
        """

        style = widget.style() if widget else QtGui.QApplication.style()

        is_flat = button_option.features & QtGui.QStyleOptionButton.Flat
        if not is_flat:
            style.proxy().drawControl(
                QtGui.QStyle.CE_PushButtonBevel, button_option, painter
            )

        subopt = QtGui.QStyleOptionButton(button_option)
        subopt.rect = style.subElementRect(
            QtGui.QStyle.SE_PushButtonContents, button_option, widget
        )
        style.proxy().drawControl(QtGui.QStyle.CE_PushButtonLabel, subopt, painter)
        if button_option.state & QtGui.QStyle.State_HasFocus:
            fropt = QtGui.QStyleOptionFocusRect()
            fropt.backgroundColor = self.get_option_background_brush(
                button_option
            ).color()
            fropt.palette = button_option.palette
            fropt.state = button_option.state
            fropt.fontMetrics = button_option.fontMetrics
            fropt.rect = style.subElementRect(
                QtGui.QStyle.SE_PushButtonFocusRect, button_option, widget
            )
            style.proxy().drawPrimitive(QtGui.QStyle.PE_FrameFocusRect, fropt, painter)

    def _init_style_option(
        self, style_option, view_option, widget, action, rect, index_data
    ):
        """
        Initialize the style option to render the index action.

        :param style_option: The style option used for rendering the item. This will be specific to the
            element to be drawn (e.g. QStyleOptionButton, QStyleOptionProgressBar, etc.).
        :type style_option: :class:`sgtk.platform.qt.QtGui.QStyleOption`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param widget: Set this widget for the style option to inherit the style from.
        :type widget: QtGui.QWidget
        :param action: The action to draw the push button for
        :type action: ViewItemAction
        :param rect: The action's bounding rect
        :type rect: QRect
        :param index_data: The specifici data for the action and the index being rendered
        :type index_data: dict
        """

        if widget:
            style_option.initFrom(widget)

        style_option.fontMetrics = view_option.fontMetrics
        style_option.palette = view_option.palette
        style_option.rect = rect
        style_option.state = index_data.get(
            "state", QtGui.QStyle.State_Active | QtGui.QStyle.State_Enabled
        )

        # Add the hover state, if the current cursor position intersects the action rect.
        is_hover = self._hit_box_test(view_option, rect)
        if is_hover:
            style_option.state |= QtGui.QStyle.State_MouseOver

        # TODO find a better way to specifiy the palette color based on button state.
        # e.g. is there a way leverage the palette color group and roles?
        if action.palette_brushes:
            if is_hover:
                brushes = action.palette_brushes["hover"]
            else:
                brushes = action.palette_brushes["active"]

            for (color_group, color_role, brush) in brushes:
                style_option.palette.setBrush(color_group, color_role, brush)

    def _get_action_progress_bar_option(
        self, view_option, widget, action, rect, index_data
    ):
        """
        Initialize the progress bar style option to render the index action.

        :param style_option: The style option used for rendering the item. This will be specific to the
            element to be drawn (e.g. QStyleOptionButton, QStyleOptionProgressBar, etc.).
        :type style_option: :class:`sgtk.platform.qt.QtGui.QStyleOption`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param widget: Set this widget for the style option to inherit the style from.
        :type widget: QtGui.QWidget
        :param action: The action to draw the push button for
        :type action: ViewItemAction
        :param rect: The action's bounding rect
        :type rect: QRect
        :param index_data: The specifici data for the action and the index being rendered
        :type index_data: dict
        """

        progress_bar_option = QtGui.QStyleOptionProgressBar()
        self._init_style_option(
            progress_bar_option, view_option, widget, action, rect, index_data
        )

        progress_bar_option.minimum = index_data.get("minimum", 0)
        progress_bar_option.maximum = index_data.get("maximum", 100)
        progress_bar_option.progress = index_data.get("progress", -1)
        progress_bar_option.text = index_data.get("text", "")
        progress_bar_option.textVisible = index_data.get("text_visible", False)
        progress_bar_option.textAlignment = index_data.get(
            "text_alignment", QtCore.Qt.AlignLeft
        )
        progress_bar_option.bottomToTop = index_data.get("bottom_to_top", False)
        progress_bar_option.invertedAppearance = index_data.get(
            "inverted_appearance", False
        )

        return progress_bar_option

    def _get_action_button_option(self, view_option, widget, action, rect, index_data):
        """
        Initialize the button style option to render the index action.

        :param style_option: The style option used for rendering the item. This will be specific to the
            element to be drawn (e.g. QStyleOptionButton, QStyleOptionProgressBar, etc.).
        :type style_option: :class:`sgtk.platform.qt.QtGui.QStyleOption`
        :param view_option: The option used for rendering the item.
        :type view_option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param widget: Set this widget for the style option to inherit the style from.
        :type widget: QtGui.QWidget
        :param action: The action to draw the push button for
        :type action: ViewItemAction
        :param rect: The action's bounding rect
        :type rect: QRect
        :param index_data: The specifici data for the action and the index being rendered
        :type index_data: dict
        """

        button_option = QtGui.QStyleOptionButton()
        self._init_style_option(
            button_option, view_option, widget, action, rect, index_data
        )

        button_option.text = index_data.get("name", action.name)

        # Set the action icon
        icon = index_data.get("icon", action.icon)
        if icon:
            icon_size = index_data.get("icon_size") or action.icon_size
            button_option.icon = icon
            button_option.iconSize = icon_size

        # Apply any additional features defined by the action.
        if action.features:
            button_option.features |= action.features

        # Icons and checkboxes are rendered as flat buttons
        if action.type in (ViewItemAction.TYPE_ICON, ViewItemAction.TYPE_CHECK_BOX):
            button_option.features |= QtGui.QStyleOptionButton.Flat

        # Override palette to invert text color for flat buttons it have a higher contrast
        if button_option.features & QtGui.QStyleOptionButton.Flat:
            is_hover = button_option.state & QtGui.QStyle.State_MouseOver
            if not is_hover or action.callback is None:
                brush = button_option.palette.light()
            else:
                brush = button_option.palette.buttonText()
            button_option.palette.setBrush(QtGui.QPalette.ButtonText, brush)
            button_option.palette.setBrush(QtGui.QPalette.Window, brush)

        # Override the palette for disabled buttons
        # This is a work aroudn because the QStyle draw methods do not seem to render the
        # "disabled" state for the button, even when the palette "Disabled" color group is set
        if button_option.state & QtGui.QStyle.State_Enabled:
            # Button enabled - leave the palette as is
            pass
        else:
            # Button disabled - set the button and button text brushes to render a 'greyed out' look
            disabledButtonText = button_option.palette.buttonText()
            disabledButtonTextColor = disabledButtonText.color()
            disabledButtonTextColor.setAlpha(50)
            disabledButtonText.setColor(disabledButtonTextColor)
            button_option.palette.setBrush(
                QtGui.QPalette.ButtonText, disabledButtonText
            )

        return button_option

    def _draw_tooltip(self, option, rect, text):
        """
        Show a tooltip at the current cursor position, if it is hovering over the given rect.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param rect: The rect to check if the cursor is over.
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`
        :param text: The tooltip text to display.
        :type text: str
        """

        cursor_pos = self.get_cursor_pos(option)
        widget = self.get_option_widget(option)

        if cursor_pos and rect.contains(cursor_pos):
            global_pos = QtGui.QCursor().pos()
            QtGui.QToolTip.showText(global_pos, text, widget, rect)

    def _draw_text_tooltip(self, option, rect, index, elided=None):
        """
        Show a tooltip for the item's text if it has been elided or clipped. Text tooltips will
        only be drawn if:
            1. The `show_text_tooltip` property is True
            2. The `override_item_tooltip` property is True or the item does not have a tooltip

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param rect: The rect to check if the cursor is over.
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param elided: True if the text has already been processed and is elided, else False. If
                       set to None, the text has not been processed.
        """

        # Only show tooltips if enabled and the cursor is hovering
        if not self.show_text_tooltip or not self.is_hover(option):
            return

        try:
            # Try to get the item associated with this index, to check if it has a tooltip set.
            if isinstance(index.model(), QtGui.QSortFilterProxyModel):
                source_index = index.model().mapToSource(index)
                item = source_index.model().itemFromIndex(source_index)
            else:
                item = index.model().itemFromIndex(index)

            item_tooltip = item.toolTip()
        except AttributeError:
            # Failed to extract the tooltip from the index .
            item = None
            item_tooltip = None

        if self._override_item_tooltip or not item_tooltip:
            # Tooltip override was set or the item does not have a tooltip, so show our tooltip
            # with the full text if it was elided, or clipped and auto-expand is disabled.

            if elided is None:
                # Text has not yet been processed for eliding, let's check here.
                _, elided = self._get_text_document(option, index, rect)
                if not elided:
                    # FIXME header eliding is not detected in the _get_text_document method
                    _, elided = self._get_header_text(
                        index, option, rect, return_elided=True
                    )

            clipped = False
            if not elided and self.expand_role is None:
                # Auto-expand disabled, check if text clipped.
                text = self._get_text(index)
                clipped = self._is_text_clipped(option, rect, text)

            if elided or clipped:
                # Override the item tooltip by clearing it before showing the tooltip we want.
                if item and item_tooltip:
                    item.setToolTip(None)

                # Show plain text in the tooltip, remove any trailing white space and ensure single line spacing.
                full_text = self.get_displayed_text(index).strip().replace("\n\n", "\n")
                QtCore.QTimer.singleShot(
                    500,
                    lambda o=option, r=rect, t=full_text: self._draw_tooltip(o, r, t),
                )

    ######################################################################################################
    # Getter methods to retrieve the item data to display. Override any of these methods to customize the
    # data that is rendered for an item.

    def _get_thumbnail(self, index):
        """
        Get the thumbnail for the item.

        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The item thumbnail data
        :rtype: :class:`sgtk.platform.qt.QtGui.QPixmap`
        """

        thumbnail = self.get_value(index, self.thumbnail_role)

        if thumbnail is None:
            return None

        if not thumbnail:
            # Default to empty pixmap
            thumbnail = QtGui.QPixmap(
                ":/tk-framework-qtwidgets/shotgun_widget/rect_512x400.png"
            )

        if isinstance(thumbnail, QtGui.QIcon):
            thumbnail = self._convert_icon_to_pixmap(thumbnail)

        if not thumbnail or not isinstance(thumbnail, QtGui.QPixmap):
            return None

        return thumbnail

    def _get_text(self, index, option=None, rect=None):
        """
        Return the text data to display. The text data will be the concatentation of the
        data retrieved from the header_role, subtitle_role and text_role.

        :param index: The item model index.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param option: The option used for rendering the item. When specified with `rect`,
                       the header text will be elided, if necessary.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param rect: The bounding rect for the text. When specified with `option`, the
                     header text will be elided, if necessary.
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`

        :return: A list, where each item represents a text line in the item's whole text.
        :rtype: list<str>
        """

        return [
            self._get_header_text(index, option, rect)
        ] + self.get_display_values_list(index, self.text_role)

    def _get_header_text(self, index, option=None, rect=None, return_elided=False):
        """
        Return the header text data to display.

        This will get the data from the `header_role`
        and `subtitle_role`, and format them into a single line using an HTML table tag. The
        table is required to format the subtitle to align right within the same text line as
        the header text.

        When the option and rect parameters are provided, the header and subtitle text will
        be elided, if necessary. Eliding the text must occur here, and not later on in the
        text processing cycle since the `_elide_text` method cannot handle eliding text inside
        an HTML table tag very nicely, nor does Qt support eliding text in tables using the
        HTML/CSS attributes.

        :param index: The item model index.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param option: The option used for rendering the item. When specified with `rect`,
                       the header text will be elided, if necessary.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param rect: The bounding rect for the text. When specified with `option`, the
                     header text will be elided, if necessary.
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`
        :param return_elided: Flag indicating whether or not to return a tuple including the
                              text with a boolean flag indicating if the text was elided or not.
        :type return_elideD: bool (defualt is False)

        :return: The formatted header text, as well as a boolean flag indicating if the header
                 text was elided.
        :rtype: tuple<str,bool>

        """

        elided = False
        title = self.get_display_values_list(index, self.header_role, flat=True) or ""
        subtitle = (
            self.get_display_values_list(index, self.subtitle_role, flat=True) or ""
        )

        if not title and not subtitle:
            # No title or subtitle found, just return an empty string.
            return ("", elided) if return_elided else ""

        title_html = ""
        subtitle_html = ""

        do_elide = self.elide_header and option and rect and rect.isValid()
        if do_elide:
            # FIXME for now we've just picked an arbitrary value to account for the HTML table offset
            # to the available width for the text
            target_width = rect.width() - 20
        else:
            target_width = -1

        if not subtitle:
            # There is only a title
            if do_elide:
                # Elide the title when the option and rect are provided, and there is text overflow.
                _, elided_title = self._get_elided_text(option, target_width, title)
                elided = title != elided_title
                title = six.ensure_str(elided_title)

            title_html = '<td align="left width="100%"">{text}</td>'.format(text=title)

        elif not title:
            # There is only a subtitle
            if do_elide:
                # Elide the title when the option and rect are provided, and there is text overflow.
                _, elided_subtitle = self._get_elided_text(
                    option, target_width, subtitle
                )
                elided = subtitle != elided_subtitle
                subtitle = six.ensure_str(elided_subtitle)

            subtitle_html = '<td align="right" width="100%">{text}</td>'.format(
                text=subtitle
            )

        else:
            # There is a title and subttile
            title_width_str = ""
            subtitle_width_str = ""

            if do_elide:
                # Elide the title and subttile when the option and rect are provided, and there
                # is text overflow.
                title_ideal_width = self._html_text_width(option, title)
                subtitle_ideal_width = self._html_text_width(option, subtitle)

                if (title_ideal_width + subtitle_ideal_width) > target_width:
                    # There is overflow, title and or subtitle should be elided.
                    title_width_pct = title_ideal_width / target_width
                    subtitle_width_pct = subtitle_ideal_width / target_width

                    if title_width_pct > 0.5 and subtitle_width_pct > 0.5:
                        # Title and subtitle are fighting for space, just split it in half.
                        title_width = 0.5 * target_width
                        subtitle_width = 0.5 * target_width
                        title_width_str = 'width="50%"'
                        subtitle_width_str = 'width="50%"'

                    elif subtitle_width_pct <= 0.5:
                        # The subtitle takes up less than half of the space, extend the title to
                        # the subtitle, and elide it if it still has overflow.
                        title_width_pct = 1.0 - subtitle_width_pct
                        title_width = title_width_pct * target_width
                        subtitle_width = subtitle_width_pct * target_width
                        title_width_str = 'width="{}%"'.format(
                            int(title_width_pct * 100)
                        )
                        subtitle_width_str = 'width="{}%"'.format(
                            int(subtitle_width_pct * 100)
                        )

                    else:
                        # The title takes up less than half of the space, extend the subtitle to
                        # the title, and elide it if it still has overflow.
                        title_width = title_width_pct * target_width
                        subtitle_width_pct = 1.0 - title_width_pct
                        subtitle_width = subtitle_width_pct * target_width
                        title_width_str = 'width="{}%"'.format(
                            int(title_width_pct * 100)
                        )
                        subtitle_width_str = 'width="{}%"'.format(
                            int(subtitle_width_pct * 100)
                        )

                    _, elided_title = self._get_elided_text(option, title_width, title)
                    _, elided_subtitle = self._get_elided_text(
                        option, subtitle_width, subtitle
                    )
                    elided = title != elided_title or subtitle != elided_subtitle
                    title = six.ensure_str(elided_title)
                    subtitle = six.ensure_str(elided_subtitle)

            title_html = '<td align="left" {width}>{text}</td>'.format(
                width=title_width_str, text=title
            )
            subtitle_html = '<td align="right" {width}>{text}</td>'.format(
                width=subtitle_width_str, text=subtitle
            )

        # The final formatted text
        formatted_header = (
            '<table width="100%" cellpadding="0" cellspacing="0" border="{border}"><tr>{title_cell}{subtitle_cell}</tr></table>'
        ).format(
            title_cell=title_html,
            subtitle_cell=subtitle_html,
            border="1" if DEBUG_PAINT else "none",
        )

        return (formatted_header, elided) if return_elided else formatted_header

    def _get_text_document(self, option, index, rect, clip=True):
        """
        Return the QTextDocument that contains the index text data to display. A
        QTextDocument is used in order to support HTML/rich text, as well as
        keeping all text inside a single object, so that it is easier to manage
        the bounding rect and size of the text.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The item model index.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param rect: The bounding rect for the text.
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`

        :return: A tuple containing the text document containing all text for the item and
                 a flag indicating if any of the text was elided during formatting.
        :rtype: tuple<:class:`sgtk.platform.qt.QtGui.QTextDocument`, bool>
        """

        text = self._get_text(index, option, rect)
        html, elided = self._format_html_text(option, index, rect, text, clip)

        doc = self._create_text_document(option)
        if rect.isValid() and rect.width() > 0:
            doc.setTextWidth(rect.width())

        doc.setHtml(html)

        return (doc, elided)

    def _get_actions(self, option, index, return_all=False, positions=None):
        """
        Retun all of the actions that are valid for this item.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The item model index.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param return_all: Return all actions no matter what.
        :type return_all: bool
        :param positions: A list of positions to retrieve actions from.
        :type positions: list<POSITION>, where POSITION is one of the positions
                         in `POSITIONS`.

        :return: All of the valid actions for the item.
        :rtype: dict, mapping position to list of actions in that position.
        """

        result = {}
        positions = positions or []
        selected = self.is_selected(option)
        hover = self.is_hover(option)

        for pos, _ in enumerate(self.POSITIONS):
            if positions and pos not in positions:
                continue

            result[pos] = []

            for action in self._actions.get(pos, []):
                if (
                    return_all
                    or action.show_always
                    or (selected and action.show_on_selected)
                    or (hover and action.show_on_hover)
                ) and action.is_visible(self.parent(), index):
                    # Action is valid for this item
                    result[pos].append(action)

        return result

    def _get_action_and_rects(self, option, index, return_all=False, positions=None):
        """
        Return a list of tuples of the view item actions and their respective rect.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The item model index.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param return_all: Return all actions no matter what.
        :type return_all: bool
        :param positions: A list of positions to retrieve actions from.
        :type positions: list<POSITION>, where POSITION is one of the positions
                         in `POSITIONS`.

        :return: All of the valid actions for the item and their respective bounding rect.
        :rtype: list<tuple<action, bouding_rect>>
        """

        rects = []
        item_action_data = self._get_actions(option, index, return_all, positions)

        for position, actions in item_action_data.items():
            # The offset will indicate where the next action bounding rect should start.
            offset = self.action_item_margin

            for action in actions:
                # Get the bounding rect for this action
                rect = self._get_action_rect(option, index, position, offset, action)
                # Increment the offset to get the next action boudning rect.
                offset += rect.width() + self.action_item_margin
                rects.append((action, rect))

        return rects

    ######################################################################################################
    # Getter methods for bounding rects for item data. Override any of these methods to customize the size
    # and positioning of the item data; e.g. see the ThumbnailViewItemDelegate that subclasses this base class
    # to reposition the thumbnail on top and text undernearth (instead of thumbnail left and text to the right.

    def _get_loading_rect(self, option, index):
        """
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

        origin = QtCore.QPoint(
            option.rect.right() - self.action_item_margin - self.icon_size.width(),
            option.rect.top()
            + (option.rect.height() / 2)
            - (self.icon_size.height() / 2),
        )

        return QtCore.QRect(origin, self.icon_size)

    def _get_thumbnail_rect(self, option, index, thumbnail=None):
        """
        Return the boudning rect for the item's thumbnail. The bounding rect will be
        positioned on the left of the option rect.

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

        # Set the thumbnail rect size to the size of the thumbnail, after it has been scaled
        # to fit to the option rect height.
        height = option.rect.height()
        thumbnail = thumbnail.scaledToHeight(height)

        if self.thumbnail_width < 0:
            width = thumbnail.width()
        else:
            width = self.thumbnail_width

        rect.setSize(QtCore.QSize(width, height))

        # Bump the thumbnail to the left, if there are non-floating actions on the left.
        dx = (
            self._get_actions_left_offset(option, index, include_margin=True)
            + self.thumbnail_padding.left
        )
        dx2 = self.thumbnail_padding.right
        dy = self.thumbnail_padding.top
        dy2 = self.thumbnail_padding.bottom
        rect.adjust(dx, dy, -dx2, -dy2)

        return rect

    def _get_text_rect(self, option, index):
        """
        Returns the bounding rect for the view item text. The rect will be
        positioned to the right of the thumbnail rect and span the height
        of option's rect and span the rest of the option rect width.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The bounding rect for the item text.
        :rtype: :class:`sgtk.platform.qt.QtCore.QRect`
        """

        rect = QtCore.QRect(option.rect)

        thumbnail_rect = self._get_thumbnail_rect(option, index)
        if thumbnail_rect.isValid():
            # Just set the rect left edge to the thumbnail rect right edge.
            rect.setLeft(thumbnail_rect.right())
            dx = 0
        else:
            # Get the actions offset from the left to adjust the text rect.
            dx = self._get_actions_left_offset(option, index, include_margin=False)
        dx += self.text_padding.left

        # Get the actions offset from the right to adjust to the text rect.
        dx2 = self._get_actions_right_offset(option, index, include_margin=False)

        loading_rect = self._get_loading_rect(option, index)
        if loading_rect.isValid():
            # Adjust the rect to the left, when displaying the loading indicator.
            dx2 = max(dx2, loading_rect.width() + self.action_item_margin)
        dx2 += self.text_padding.right

        dy = self.text_padding.top
        dy2 = self.text_padding.bottom
        rect.adjust(dx, dy, -dx2, -dy2)
        return rect

    def _get_action_rect(self, option, index, position, offset, action):
        """
        Returns the bounding rect for the view item action.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param position: The position of the action
        :type position: POSITION enum
        :param offset: The horizontal offset from the action's position starting point;
                       for example, if the position is TOP_RIGHT corner, then the offset
                       is how far to the left of the rect top right corner, that the action
                       should be drawn.
        :param action: The action to get the bounding rect for.
        :type action: :class:`ViewItemAction`

        :return: The bounding rect for the item action.
        :rtype: :class:`sgtk.platform.qt.QtCore.QRect`
        """

        index_data = action.get_data(self.parent(), index)
        name = index_data.get("name", action.name)
        icon = index_data.get("icon", action.icon)
        icon_size = index_data.get("icon_size") or action.icon_size

        if index_data.get("width", None) == "100%":
            width = option.rect.width()
        else:
            # Calculate the width of the action
            width = index_data.get(
                "padding_left", action.get_padding_left()
            ) + index_data.get("padding_right", action.get_padding_right())

            # Extend the width for the text
            if name:
                width += option.fontMetrics.width(name) + 5

            # Extend the width for the icon
            if icon:
                width += icon_size.width()

            # Extend the width for by the width hint
            width += index_data.get("width", action.width_hint())

        # Set the height to the height of a single text line, plus padding.
        height = index_data.get(
            "padding_top", action.get_padding_top()
        ) + index_data.get("padding_bottom", action.get_padding_bottom())
        if index_data.get("adjust_height_to_icon", False):
            height += icon_size.height()
        else:
            height += option.fontMetrics.height()

        # Calculate the top left (origin) point, based on the position and offset, to draw the action rect
        if position in (self.TOP_LEFT, self.FLOAT_TOP_LEFT):
            origin = QtCore.QPoint(
                option.rect.left() + offset,
                option.rect.top() + self.action_item_margin,
            )
        elif position in (self.TOP_RIGHT, self.FLOAT_TOP_RIGHT):
            origin = QtCore.QPoint(
                option.rect.right() - offset - width,
                option.rect.top() + self.action_item_margin,
            )
        elif position in (self.BOTTOM_LEFT, self.FLOAT_BOTTOM_LEFT):
            origin = QtCore.QPoint(
                option.rect.left() + offset,
                option.rect.bottom() - height - self.action_item_margin,
            )
        elif position in (self.BOTTOM_RIGHT, self.FLOAT_BOTTOM_RIGHT):
            origin = QtCore.QPoint(
                option.rect.right() - offset - width,
                option.rect.bottom() - height - self.action_item_margin,
            )
        elif position in (self.LEFT, self.FLOAT_LEFT):
            origin = QtCore.QPoint(
                option.rect.left() + offset,
                option.rect.top() + (option.rect.height() / 2) - (height / 2),
            )
        elif position in (self.RIGHT, self.FLOAT_RIGHT):
            origin = QtCore.QPoint(
                option.rect.right() - offset - width,
                option.rect.top() + (option.rect.height() / 2) - (height / 2),
            )
        elif position == self.CENTER:
            origin = QtCore.QPoint(
                option.rect.left() + (option.rect.width() / 2) - (width / 2),
                option.rect.top() + (option.rect.height() / 2) - (height / 2),
            )
        else:
            assert False, "Unsupported action position '{}'".format(position)

        return QtCore.QRect(origin, QtCore.QSize(width, height))

    def _get_actions_position_width(self, option, index, position):
        """
        Return the width of for all actions combined in the given position.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param position: The position of the action
        :type position: POSITION enum

        :return: The width of the row of actions in the given position.
        :rtype: int
        """

        width = 0
        actions = self._get_action_and_rects(option, index, positions=[position])
        for _, action_rect in actions:
            width += action_rect.width() + self.action_item_margin

        return width

    def _get_actions_maximum_height(self, option, index):
        """
        Return the maximum height of all actions.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The maximum height value of all the actions.
        :rtype: int
        """

        height = 0
        actions = self._get_action_and_rects(option, index, return_all=True)
        for _, action_rect in actions:
            height = max(height, action_rect.height())

        return height + self.action_item_margin

    def _get_actions_left_offset(self, option, index, include_margin=False):
        """
        Convenience method to get the offset from the left side actions. This will return the
        horizontal offset from the left of the option rect, where the actions on the left side
        span to.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param include_margin: Add margin to actions offset.
        :type include_margin: bool

        :return: The horizontal offset from the left side of the option rect where the left
                 side actions end.
        :rtype: int
        """

        return self._get_actions_offset(
            option, index, (self.LEFT, self.TOP_LEFT, self.BOTTOM_LEFT), include_margin
        )

    def _get_actions_right_offset(self, option, index, include_margin=False):
        """
        Convenience method to get the offset from the right side actions. This will return the
        horizontal offset from the right of the option rect, where the actions on the right side
        span to.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param include_margin: Add margin to actions offset.
        :type include_margin: bool

        :return: The horizontal offset from the right side of the option rect where the right
                 side actions end.
        :rtype: int
        """

        return self._get_actions_offset(
            option, index, (self.RIGHT, self.TOP_RIGHT, self.BOTTOM_RIGHT)
        )

    def _get_actions_offset(self, option, index, positions, include_margin=False):
        """
        Convenience method to get the offset for the actions in the given positions. This will
        return the offset from the edge of the option rect, to how far the actions span.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param position: The positions of the actions to calculate the offset for. When more than one
                         position is provided, the positions should be oriented from the same side (e.g.
                         top left, bottom left and left).
        :type position: tuple<POSITION>, where POSITION is one of the position enums
        :param include_margin: Add margin to actions offset.
        :type include_margin: bool

        :return: The offset from the edge of the option rect to how far the actions span.
        :rtype: int
        """

        offset = max(
            [self._get_actions_position_width(option, index, pos) for pos in positions]
        )

        if offset > 0:
            # Add the margin from the option rect to the first action.
            if include_margin:
                # Optionally add margin at the end of the actions.
                offset += self.action_item_margin

        return offset

    ######################################################################################################
    # Private methods

    def _hit_box_test(self, option, rect):
        """
        Return True if the current cursor position intersects the given rect. If mouse tracking
        is not enabled on the option widget, this will always return False.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param rect: The rect to check if the cursor is over.
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`

        :return: True if the current cursor position intersects the given rect, else False.
        :rtype: bool
        """

        cursor_pos = self.get_cursor_pos(option)
        return cursor_pos and rect.contains(cursor_pos)

    def _action_at(self, option, index, pos):
        """
        Return the action at the given point `pos`.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param pos: The point to check intersection with action bounding rect.
        :type pos: :class:`sgtk.platform.qt.QtCore.QPoint`

        :return: The aciton found at point `pos`.
        :rtype: :class:`ViewItemAction`
        """

        actions_and_rects = self._get_action_and_rects(option, index, return_all=True)

        # Check for actions in reverse order, since the actions added last will appear in the "front"
        for action, rect in actions_and_rects[::-1]:
            if rect.contains(pos):
                return action

        return None

    def _convert_icon_to_pixmap(self, icon):
        """
        Return the pixmap converted from the given icon.

        :param icon: The icon to conver to a pixmap.
        :type icon: :class:`sgtk.platform.qt.QtGui.QIcon`

        :return: The pixmap converted from the icon.
        :rtype: :class:`sgtk.platform.qt.QtGui.QPixmap`
        """

        return icon.pixmap(self.pixmap_extent) if icon else None

    def _update_index_expand_state(self, option, index):
        """
        Check if an item expand state should change (expand to show all text or collapse
        to hide text).

        If the cursor is hovering over the item or the item is selected, and the item
        text is clipped, then set the index model data to signal to the delegate to
        expand the item height to show all text.

        If the cursor is not hovering over the item and the item was expanded to show all text, now collapse the item.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: True if the item exapnd state was changed (either expanded or collapsed).
        :rtype: bool
        """

        if self.expand_role is None:
            return False

        text = self._get_text(index)
        text_rect = self._get_text_rect(option, index)
        clipped = self._is_text_clipped(option, text_rect, text)
        is_expanded = self.get_value(index, self.expand_role)

        state_changed = False
        hover = self.is_hover(option)
        selected = self.is_selected(option)
        if (hover or selected) and clipped and not is_expanded:
            # Cursor is hovering over an item, or item is selected, and its text is vertically
            # clipped. Set the index data flag to expand the row height.
            self._toggle_expand_item(index, True)
            state_changed = True

        elif not (hover or selected) and not clipped and is_expanded:
            # This item was expanded on hover or due to selection, but now is deselected or the
            # cursor has moved off of it. Update the index data to collapse the item height.
            self._toggle_expand_item(index, False)
            state_changed = True

        return state_changed

    def _toggle_expand_item(self, index, expand_flag=None):
        """
        Expand the item to display all text. To expand the item, the item index data
        will be set to indicate that the item should expand to display all of its
        text data, then a `sizeHintChanged` signal is emitted to re-render the item.

        :param index: The model index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        """

        if self.expand_role is None:
            return

        if expand_flag is None:
            expand_flag = not self.get_value(index, self.expand_role)

        index.model().setData(index, expand_flag, self.expand_role)
        self.sizeHintChanged.emit(index)

    def _is_expanded(self, index):
        """
        Returns True if the item is currently expanded to show all text.

        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: True if the expand action is currently shown, else False.
        :rtype: bool
        """

        return self.expand_role and self.get_value(index, self.expand_role)

    def _create_text_document(self, option):
        """
        Return a new QTextDocument object. Whenever a QTextDocument is required, this
        method should be used to create the object to ensure all QTextDocuments used
        for the item text are consistent (e.g. font, document margin, etc.).

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`

        :return: The created QTextDocument object.
        :rtype: :class:`sgtk.platform.qt.QtGui.QTextDocument`
        """

        doc = QtGui.QTextDocument()
        # Use the font set on the delegate. If not set, default to theoption font is initialized
        # in the QStyledItemDelegate `initStyleOption` method, the font is set based on the model
        # index data for the QtCore.Qt.FontRole.
        doc.setDefaultFont(self.font or option.font)
        doc.setDefaultStyleSheet(self.document_style_sheet)
        doc.setDocumentMargin(self.text_document_margin)

        text_option = QtGui.QTextOption(doc.defaultTextOption())
        text_option.setWrapMode(QtGui.QTextOption.WordWrap)
        doc.setDefaultTextOption(text_option)

        return doc

    def _get_visible_lines_height(self, option, line_text="placeholder"):
        """
        Return the height based on the number of visible lines. A placeholder text is used
        to calculate the height per line.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param line_text: The placehoder text used to calculate the line height. The specific
                          text should not affect the overall height.
        :type line_text: str

        :return: The height calculated from the number of visible lines that are displayed.
        :rtype: int
        """

        if self.visible_lines <= 0:
            return 0

        # A QTextDocument is created to calculate an accurate height to what would be rendered.
        doc = self._create_text_document(option)

        # Create an HTML text string that is the number of `visible_lines`
        html_lines = "<br/>".join([line_text] * self.visible_lines)

        doc.setHtml(html_lines)
        return doc.size().height()

    def _html_text_width(self, option, text):
        """
        Return the width of the rendered HTML text.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param text: The text to check for overflow.
        :type text: str

        :return: The width of the text when rendered.
        :rtype: int
        """

        # To calculate the width of the HTML text, a QTextDocument is reuired to ensure
        # that any formatting on the text is applied when getting the text width.
        doc = self._create_text_document(option)
        doc.setHtml(text)

        return doc.idealWidth()

    def _is_text_clipped(self, option, rect, text_lines):
        """
        Returns True if the displayed text was vertically clipped to fit
        to the view item bounding rect.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param rect: The text bounding rect
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`
        :param text_lines: The text to check if it fits inside the given rect,
                           if not, it should be clipped.
        :type text_line: list<str>

        :return: True if the text has overflow and should be clipped, else False.
        :rtype: bool
        """

        line_num = 0
        height = 0
        text_doc_margins = 2 * self.text_document_margin
        # The maximum height for the text
        available_height = rect.height() - text_doc_margins

        # Go through the text lines one by one, adding up each line height and
        # returning True immediately if the text goes beyond the rect height.
        while line_num < len(text_lines):  # and height < rect.height():
            # while line_num < len(text_lines) and height < rect.height():
            line = text_lines[line_num].strip()
            line_num += 1

            if not line or not isinstance(line, six.string_types):
                continue

            # Split the line if there are any HTML line breaks in the text.
            html_text_lines = self.split_html_lines(line)
            for text in html_text_lines:
                text = text.strip()
                if not text:
                    continue

                # No need to elide the text, the text line height will remain the same.
                text_line_doc = self._create_text_document(option)
                text_line_doc.setHtml(text)

                # Append the text line height and substract the text doc margin since when the text
                # is actually rendered, it will be rendered in one text document, instead of a
                # text document per line (text document in this case needs to be created per line
                # to calculate the individual line heights).
                height += text_line_doc.size().height() - text_doc_margins
                if height > available_height:
                    # Text exceeds the maximum height, indicate the text should be clipped.
                    return True

        # Text fits within the available rect height.
        return False

    def _format_html_text(self, option, index, rect, text_lines, clip):
        """
        Format the HTML text.

        :param option: The option used for rendering the item.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param index: The index of the item.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param rect: The text bounding rect
        :type rect: :class:`sgtk.platform.qt.QtCore.QRect`
        :param text_lines: The text to check if it fits inside the given rect,
                           if not, it should be clipped.
        :type text_line: list<str>
        :param clip: True if the text should be clipped when there is overflow, else False
                     will return all text even if there is overflow.

        :return: A tuple containging the html formatted text and a flag indicating if the
                 any of the text was elided during formatting.
        :rtype: tuple<str, bool>
        """

        html_lines = []
        line_count = 0
        line_num = 0
        elided = False

        if clip:
            # Keep track of the height when the text will be clipped if exceeds the maximum height.
            height = 0
            margin_offset = 2 * self.text_document_margin
            # The maximum allowed text height.
            available_height = rect.height() - margin_offset

        # Format text line by line
        # Stop if clipping enabled and the text height exceeds the maximum
        # Stop if `visible_lines` property is set and the line count exceeds the number of visible lines set and the
        #   item for this index is not expanded (e.g. do not clip if item is set to be expanded to show all text)
        while (
            line_num < len(text_lines)
            and (not clip or height < rect.height())
            and (
                self.visible_lines < 0
                or self._is_expanded(index)
                or line_count < self.visible_lines
            )
        ):
            line = text_lines[line_num].strip()
            line_num += 1

            if not line or not isinstance(line, six.string_types):
                continue

            # If an individual line has line breaks, split out those lines and process
            # them individually.
            html_text_lines = self.split_html_lines(line)
            for text in html_text_lines:
                # Strip any leading or trailing whitespace.
                text = text.strip()
                if not text:
                    continue

                if (
                    not self._is_expanded(index)
                    and self.visible_lines >= 0
                    and line_count >= self.visible_lines
                ):
                    # Exceeded the number of visible lines. Stop formatting.
                    break

                if self.elide_text:
                    # Because the text is allowed to be HTML formatted, in order to elide an
                    # individual line (if necessary), the text must be rendered using a
                    # QTextDocument which then the document can be used to determine if the
                    # formatted text exceeds the maximum width. A side effect of eliding the
                    # text using a QTextDocument is that the resulting elided text will be
                    # a full HTML doc string.
                    doc, elided_text = self._get_elided_text(option, rect.width(), text)
                else:
                    # Even though the text is not elided, still need to get the text document
                    # to measure the text height for clipping
                    doc = self._create_text_document(option)
                    doc.setHtml(text)
                    elided_text = None

                if clip:
                    height += doc.size().height() - margin_offset
                    if height > available_height and clip:
                        # Text height exceeded the maximum. Stop formatting.
                        break

                if elided_text is None or text == elided_text:
                    # Text did not change, just add the text and a line break.
                    html_lines.append(text)
                    html_lines.append("<br/>")
                else:
                    # Text was elided. Elided text is in the format of a full HTML document,
                    # which includes line breaks before and after, so if there
                    # was a line break added before this line, remove it. Do not explicitly
                    # add a # new line break after the elided text.
                    if html_lines and html_lines[-1] == "<br/>":
                        html_lines[-1] = elided_text
                    else:
                        html_lines.append(elided_text)

                    elided = True

                line_count += 1

        # Remove trailing new line
        if html_lines and html_lines[-1] == "<br/>":
            html_lines = html_lines[:-1]

        # Return a single string, lines are separated by HTML line break tags.
        html_lines = [six.ensure_str(line) for line in html_lines]
        formatted_str = "".join(html_lines)
        return (formatted_str, elided)

    def _get_elided_text(
        self, option, target_width, text, elide_mode=QtCore.Qt.ElideRight
    ):
        """
        Elide the text if the width exceeds the given `target_width`. This slightly tweaks
        the implementation from :class:`ElidedLabel` method `_elide_text`.

        :param option: The view option the text is rendered in.
        :type option: :class:`sgtk.platform.qt.QtGui.QStyleOptionViewItem`
        :param target_width: The desired width for the text
        :type target_width: int
        :param text: The text to elide
        :type text: str
        :param elide_mode: The elide mode to use
        :type elide_mode: :class:`sgtk.platform.qt.Qtcore.Qt.TextElideMode`

        :returns: The QTextDocument used to elide the text and the elided text. If the text
                  is not elided, the original text is returned. Note that if the text is
                  elided, the elided text is the value returned by doc.toHtml(), which will
                  return a string in the form of a full HTML document.
        :rtype: tuple<:class:`sgkt.platform.qt.QTextDocument`, str>
        """

        # Use a QTextDocument to measure html/rich text width
        doc = self._create_text_document(option)
        doc.setHtml(text)

        if target_width < 0 or text.startswith("<table"):
            # Just return the doc and text unaltered if the target_width is invalid or the text contains
            # unsupported HTML tags.
            # NOTE: Text wrapped in HTML table tag is not supported. See `get_header_text` as an example
            # to eliding table cell text.
            return (doc, text)

        line_width = doc.idealWidth()
        if line_width <= target_width:
            # Nothing more to do, the text fits within the target_width
            return (doc, text)

        # Depending on the elide mode, insert ellipses in the correct place
        cursor = QtGui.QTextCursor(doc)
        ellipses = ""
        if elide_mode != QtCore.Qt.ElideNone:
            # Add the ellipses in the correct place
            ellipses = "..."

            if elide_mode == QtCore.Qt.ElideLeft:
                cursor.setPosition(0)
            elif elide_mode == QtCore.Qt.ElideRight:
                char_count = doc.characterCount()
                cursor.setPosition(char_count - 1)
            cursor.insertText(ellipses)

        ellipses_len = len(ellipses)

        # Remove characters until the text fits within the target width
        while line_width > target_width:
            start_line_width = line_width

            # If string is less than the ellipses length then just return an empty string
            char_count = doc.characterCount()
            if char_count <= ellipses_len:
                return ""

            # Calculate the number of characters to remove - should always remove at least 1 to be sure the text gets shorter
            line_width = doc.idealWidth()
            p = target_width / line_width
            # Play it safe and remove a couple less than the calculated amount
            chars_to_delete = max(1, char_count - int(float(char_count) * p) - 2)

            # Remove the characters:
            if elide_mode == QtCore.Qt.ElideLeft:
                start = ellipses_len
                end = chars_to_delete + ellipses_len
            else:
                # Default is to elide right
                start = max(0, char_count - chars_to_delete - ellipses_len - 1)
                end = max(0, char_count - ellipses_len - 1)

            cursor.setPosition(start)
            cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

            line_width = doc.idealWidth()
            if line_width == start_line_width:
                break

        return (doc, doc.toHtml())


class ViewItemAction(object):
    """
    Class object to handle rendering item actions in the :class:`ViewItemDelegate`.
    """

    # Enum to describe the type of view item action.
    (
        TYPE_PUSH_BUTTON,
        TYPE_RADIO_BUTTON,
        TYPE_CHECK_BOX,
        TYPE_PROGRESS_BAR,
        TYPE_ICON,
    ) = range(5)

    # Default widths for action types
    DEFAULT_WIDTHS = {
        TYPE_RADIO_BUTTON: 6,
        TYPE_PROGRESS_BAR: 100,
    }

    # The action attributes that will be used to initialize the object.
    _ATTRIBUTES = [
        {
            # The text/label displayed for the action button
            "key": "name",
            "default": "",
        },
        {
            "key": "type",
            "default": TYPE_PUSH_BUTTON,
        },
        {
            # The action button option style features
            "key": "features",
        },
        {
            # The icon displayed for the action button
            "key": "icon",
        },
        {
            # The size for the action icon
            "key": "icon_size",
            "default": QtCore.QSize(18, 18),
        },
        {
            # Padding applied around the action button
            "key": "padding",
            "default": 4,
        },
        {
            "key": "padding_top",
            "default": None,
        },
        {
            "key": "padding_right",
            "default": None,
        },
        {
            "key": "padding_bottom",
            "default": None,
        },
        {
            "key": "padding_left",
            "default": None,
        },
        {
            # Text to display in a tooltip when the cursor is over the action
            "key": "tooltip",
        },
        {
            # Specific palette brushes to set for the action button. Palette brushes
            # dict maps brush type to list of brush items, which should be in the
            # format of a tuple, e.g.:
            #   (QPalette.ColorGroup, QPalette.ColorRole, QBrush)
            "key": "palette_brushes",
            "default": {},
        },
        {
            # Flag indicating if this action should always been shown, no matter what the state is
            "key": "show_always",
            "default": False,
        },
        {
            # Flag indicating to show the action when the action's item is selected
            "key": "show_on_selected",
            "default": True,
        },
        {
            # Flag indicating to show the action when the action's item is hovered over
            "key": "show_on_hover",
            "default": True,
        },
        {
            # Callback function used to return data to display the action for the speicifc index.
            # The parent param is the parent of the delegate requesting the data.
            "key": "get_data",
            "default": lambda parent, index: {},
        },
        {
            # Callback function used to execute some operations when the action is "clicked"
            "key": "callback",
            "default": None,
        },
        {
            # Set a fixed width for the action
            "key": "width",
            "default": None,
        },
        {
            # Flag indicating to draw the action or not, but maintains space for the action regardless of
            # if it is drawn or not (e.g. this action acts as a spacer, which may be desirable to keep
            # actions lined up in each row of the delegate's view)
            "key": "placeholder",
            "default": False,
        },
        {
            # The Qt.ItemDataRole to use set/get the action's check state data. This is usefule if an
            # item has more than one checkable action
            "key": "check_state_role",
            "default": QtCore.Qt.CheckStateRole,
        },
    ]

    def __init__(self, data):
        """
        Constructor. Use the data passed to initialize the object.

        :param data: The data to initialize the action with.
        :type data: dict, see `_ATTRIBUTES` for supported key-values.
        """

        for attribute in self._ATTRIBUTES:
            required = attribute.get("required", False)
            attr_name = attribute["key"]
            if required and attr_name not in data:
                raise ValueError(
                    "Required data not provided on {} init".format(
                        self.__class__.__name__
                    )
                )

            value = (
                data[attr_name] if attr_name in data else attribute.get("default", None)
            )
            setattr(self, attr_name, value)

    @classmethod
    def checkable_types(cls):
        """Return a tuple icontaining the types that can be checked."""
        return (cls.TYPE_CHECK_BOX, cls.TYPE_RADIO_BUTTON)

    def set_icon(self, icon):
        """
        Set the action icon. If a string is given, create the icon from the string. The icon will be
        set to None if an invalid value provided.

        :param icon: The action icon
        :type icon: str | :class:`sgkt.platform.qt.QtGui.QIcon`
        """

        if not icon:
            self.icon = None

        elif isinstance(icon, QtGui.QIcon):
            self.icon = icon

        elif isinstance(icon, six.string_types):
            self.icon = QtGui.QIcon(icon)

        else:
            self.icon = None

    def is_visible(self, parent, index):
        """
        Convenience method to check if the action is visible for the given index.

        :param parent: The parent of deleaget who requested the data.
        :type parent: :class:`sgtk.platform.qt.QtGui.QAbstractItemView`
        :param index: The model item index
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: True if the action is visible for the index.
        :rtype: bool
        """

        index_data = self.get_data(parent, index)
        return index_data.get("visible", True)

    def state(self, parent, index):
        """
        Convenience method to get the state of the action for the given index.

        :param parent: The parent of delegate who requested the data.
        :type parent: :class:`sgtk.platform.qt.QtGui.QAbstractItemView`
        :param index: The model item index
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The action state.
        :rtype: QState
        """

        index_data = self.get_data(parent, index)
        return index_data.get(
            "state", QtGui.QStyle.State_Active | QtGui.QStyle.State_Enabled
        )

    def get_name(self, parent, index):
        """
        Convenience method to get the current action name for the given index. The
        particular index may want to override the default action name.

        :param parent: The parent of deleaget who requested the data.
        :type parent: :class:`sgtk.platform.qt.QtGui.QAbstractItemView`
        :param index: The model item index
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The name for the action at the given index
        :rtype: str
        """

        index_data = self.get_data(parent, index)
        return index_data.get("name", self.name)

    def is_clickable(self, parent, index):
        """
        An action is clickable if:
            1. It is visible and not a placeholder
            2. It is a checkbox or radio action, or has a callback
            3. It is in an enabled state

        :param parent: The parent of deleaget who requested the data.
        :type parent: :class:`sgtk.platform.qt.QtGui.QAbstractItemView`
        :param index: The model item index
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: True if the action is clickable, else False.
        :rtype: bool
        """

        index_data = self.get_data(parent, index)
        if not index_data.get("visible", True) or index_data.get("placeholder", False):
            return False

        if self.callback or self.type in self.checkable_types():
            return self.state(parent, index) & QtGui.QStyle.State_Enabled

        return False

    def width_hint(self):
        """
        Get the suggested width to display the action.

        :param parent: The parent of deleaget who requested the data.
        :type parent: :class:`sgtk.platform.qt.QtGui.QAbstractItemView`
        :param index: The model item index
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The width hint for action.
        :rtype: int
        """

        return self.DEFAULT_WIDTHS.get(self.type, 0)

    def get_padding_top(self):
        """
        Return the padding for above the action.
        """

        return self.padding_top or self.padding

    def get_padding_right(self):
        """
        Return the padding to the right of the action.
        """

        return self.padding_right or self.padding

    def get_padding_bottom(self):
        """
        Return the padding for below the action.
        """

        return self.padding_bottom or self.padding

    def get_padding_left(self):
        """
        Return the padding to the left of the action.
        """

        return self.padding_left or self.padding
