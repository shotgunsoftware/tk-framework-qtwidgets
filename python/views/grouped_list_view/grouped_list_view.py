# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.
import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .grouped_list_view_item_delegate import GroupedListViewItemDelegate

class GroupedListView(QtGui.QAbstractItemView):
    """
    Custom Qt View that displays items as a grouped list.  The view works with any tree
    based model with the first level of the hierarchy defining the groups and the second
    level defining the items for that group.  Subsequent levels of the hierarchy are ignored.
    
    Items within a group are layed out left-to right and wrap automatically based on the
    view's width.
    
    For example, the following tree model::
    
        - Group 1
          - Item 1
          - Item 2
          - Item 3
        - Group 2
          - Item 4
        - Group 3
    
    Would look like this in the view::
    
        > Group 1
        -----------------
        [Item 1] [Item 2]
        [Item 3]
        > Group 2
        -----------------
        [Item 4]
        > Group 3
        -----------------
    
    The widgets used for the various groups and items are created through a GroupedListViewItemDelegate
    and this can be overriden to implement custom UI for these elements.
    """

    class _ItemInfo(object):
        """
        class representing the information that needs to be tracked for each item (row)
        in the model.
        """
        def __init__(self):
            """
            Construction
            """
            self.rect = QtCore.QRect()             # relative item rect for group header
            self.dirty = True                      # True if data in group or children has changed
            self.collapsed = False                 # True if the group is currently collapsed
            self.child_info = []                   # List of tuples containing (row, column, size) where row and
                                                   # column are the relative row and column in the visual grid and 
                                                   # size is the visual size of the child for all child items in
                                                   # the group
            self.child_area_rect = QtCore.QRect()  # total size of child area

        def __repr__(self):
            return "%s: %s" % (self.rect, self.child_area_rect)

    def __init__(self, parent):
        """
        :param parent: The parent QWidget
        :type parent:  :class:`~PySide.QtGui.QWidget`
        """
        QtGui.QAbstractItemView.__init__(self, parent)

        self._item_info = []
        self._update_all_item_info = True
        self._update_some_item_info = False
        self._max_width = 0

        # keep track of all created group widgets.  The view
        # will always try to reuse these where possible so the
        # number of created group widgets will never exceed
        # the number visible in the viewport  
        self._group_widgets = []
        self._group_widget_rows = {}

        self._prev_viewport_sz = QtCore.QSize()

        # initial values for the properties
        self._border = QtCore.QSize(6,6)
        self._group_spacing = 30
        self._item_spacing = QtCore.QSize(4,4)

        # default item delegate:
        self._default_item_delegate = GroupedListViewItemDelegate(self)

    # @property
    def _get_border(self):
        """
        The external border to use for all items in the view
        """
        return self._border
    # @border.setter
    def _set_border(self, border_sz):
        self._border = border_sz
        self._update_all_item_info = True
        self.viewport().update()
    border = property(_get_border, _set_border)

    # @property
    def _get_group_spacing(self):
        """
        The spacing to use between groups when they are collapsed
        """
        return self._group_spacing
    
    # @group_spacing.setter
    def _set_group_spacing(self, spacing):
        self._group_spacing = spacing
        self._update_all_item_info = True
        self.viewport().update()
    group_spacing = property(_get_group_spacing, _set_group_spacing)

    # @property
    def _get_item_spacing(self):
        """
        The spacing to use between items in the view
        """
        return self._item_spacing
    # @item_spacing.setter
    def _set_item_spacing(self, spacing):
        self._item_spacing = spacing
        self._update_all_item_info = True
        self.viewport().update()
    item_spacing = property(_get_item_spacing, _set_item_spacing)

    def expand(self, index):
        """
        Expand the specified index

        :param index:   The model index to be expanded
        :type index:    :class:`~PySide.QtCore.QModelIndex`
        """
        self._set_expanded(index, True)

    def collapse(self, index):
        """
        Collapse the specified index

        :param index:   The model index to be collapsed
        :type index:    :class:`~PySide.QtCore.QModelIndex`
        """
        self._set_expanded(index, False)

    def is_expanded(self, index):
        """
        Query if the specified index is expanded or not

        :param index:   The model index to check
        :type index:    :class:`~PySide.QtCore.QModelIndex`
        :returns:       True if the index is a root index and is expanded,
                        otherwise False
        """
        if not index.isValid() or index.parent() != self.rootIndex():
            return False
        row = index.row()
        if row < len(self._item_info):
            return not self._item_info[row].collapsed
        else:
            return False

    # ----------------------------------------------------------------------------------------------------
    # Overriden public methods

    def itemDelegate(self):
        """
        Overriden base method that returns the item delegate to be used for items in this
        view.  This will return the default item delegate if a delegate deriving from
        GroupedListViewItemDelegate hasn't been set for the view.

        :returns:   A class:`GroupedListViewItemDelegate` instance
        """
        delegate = QtGui.QAbstractItemView.itemDelegate(self)
        if not isinstance(delegate, GroupedListViewItemDelegate):
            # just return the defauly item delegate:
            delegate = self._default_item_delegate
        return delegate

    def edit(self, idx, trigger, event):
        """
        Override the edit method on the base class to dissalow editing 
        of group items

        :param idx:     The model index to be edited
        :param trigger: The trigger that is triggering the edit
        :param event:   The edit event
        :returns:       False if the idx is a root item (group), otherwise
                        the returned value from the base implementation
        """
        if idx.parent() == self.rootIndex():
            # we don't want to allow the regular editing of groups
            # needs to be driven by role though!
            return False
        return QtGui.QAbstractItemView.edit(self, idx, trigger, event)

    def setModel(self, model):
        """
        Overrides the base method to make sure the item info gets updated when the model
        is changed.

        :param model:   The model to set for this view
        """
        self._update_all_item_info = True
        QtGui.QAbstractItemView.setModel(self, model)

    # ----------------------------------------------------------------------------------------------------
    # Internal class methods

    def _set_expanded(self, index, expand):
        """
        Toggle the expanded state of the specified index

        :param index:   The model index to expand/collapse
        :param expand:  True if the item should be expanded, otherwise False
        """
        if not index.isValid() or index.parent != self.rootIndex():
            # can only expand valid root indexes!
            return 

        row = index.row()
        if row < len(self._item_info):
            self._item_info[row].collapsed = not expand
            self._item_info[row].dirty = True
            self._update_some_item_info = True
            self.viewport().update()

    def dataChanged(self, top_left, bottom_right):
        """
        Overriden base class method that gets called when some data in the model attached
        to this view has been changed.

        :param top_left:        The top-left model index of the data that has changed
        :param bottom_right:    The bottom-right model index of the data that has changed
        """
        #print "DATA CHANGED [%s] %s -> %s" % (top_left.parent().row(), top_left.row(), bottom_right.row())

        if top_left.parent() == self.rootIndex():
            # data has changed for top-level rows:
            for row in range(top_left.row(), bottom_right.row()+1):
                if row < len(self._item_info):
                    self._item_info[row].dirty = True
                self._update_some_item_info = True
        elif top_left.parent().parent() == self.rootIndex():
            # this assumes that all rows from top-left to bottom-right have 
            # the same parent - this seems to always be the case!
            row = top_left.parent().row()
            if row < len(self._item_info):
                self._item_info[row].dirty = True
            self._update_some_item_info = True
        else:
            self._update_all_item_info = True

        # make sure we schedule a viewport update so that everything gets updated correctly!
        self.viewport().update()
        QtGui.QAbstractItemView.dataChanged(self, top_left, bottom_right)

    def rowsInserted(self, parent_index, start, end):
        """
        Overriden base method that gets called when new rows have been inserted into
        the model attached to this view.

        :param parent_index:    The parent model index the rows have been inserted under
        :param start:           The first row that was inserted
        :param end:             The last row that was inserted
        """
        #print "ROWS INSERTED [%s] %s -> %s" % (parent_index.row(), start, end)

        if not self._update_all_item_info:
            if parent_index == self.rootIndex():
                # inserting root level rows:
                new_rows = [GroupedListView._ItemInfo() for x in range(end+1-start)]
                self._item_info = self._item_info[:start] + new_rows + self._item_info[start:]
                self._update_some_item_info = True
            elif parent_index.parent() == self.rootIndex():
                # inserting group level rows:
                parent_row = parent_index.row()
                if parent_row < len(self._item_info):
                    self._item_info[parent_row].dirty = True
                    self._update_some_item_info = True
                else:
                    self._update_all_item_info = True
            else:
                # something went wrong so refresh everything!
                self._update_all_item_info = True

        # make sure we schedule a viewport update so that everything gets updated correctly!
        self.viewport().update()
        QtGui.QAbstractItemView.rowsInserted(self, parent_index, start, end)

    def rowsAboutToBeRemoved(self, parent_index, start, end):
        """
        Overriden base method that gets called just before rows are removed from
        the model attached to this view.

        Note, not sure why but this doesn't seem to get called as expected in PyQt!  Because
        of this there is an extra validation step in self._update_item_info() which may
        slightly reduce performance in PyQt but as this only happens when items are removed
        from the model via clearing then hopefully it shouldn't be a big problem!

        :param parent_index:    The parent model index the rows have been inserted under
        :param start:           The first row that will be removed
        :param end:             The last row that will be removed
        """
        #print "ROWS REMOVED [%s] %s -> %s" % (parent_index.row(), start, end)

        if not self._update_all_item_info:
            if parent_index == self.rootIndex():
                # removing root level rows:
                self._item_info = self._item_info[:start] + self._item_info[end+1:]
                self._update_some_item_info = True
            elif parent_index.parent() == self.rootIndex():
                # inserting group level rows:
                parent_row = parent_index.row()
                if parent_row < len(self._item_info):
                    self._item_info[parent_row].dirty = True
                    self._update_some_item_info = True
                else:
                    self._update_all_item_info = True
            else:
                # something went wrong!
                self._update_all_item_info = True        

        QtGui.QAbstractItemView.rowsAboutToBeRemoved(self, parent_index, start, end)

        # make sure we schedule a viewport update so that everything gets updated correctly!
        self.viewport().update()

    def visualRect(self, index):
        """
        Overriden base method that should return the rectangle occupied by the given 
        index in the viewport

        :param index:   The model index to return the rectangle for
        :returns:       A QRect() representing the rectangle this index will occupy 
                        in the viewport
        """
        rect = QtCore.QRect()
        if index.isValid():
            item_rect = self._get_item_rect(index)
            if item_rect.isValid():
                # rectangle should be widget relative, not viewport relative:
                rect = item_rect.translated(-self.horizontalOffset(), -self.verticalOffset())
        return rect

    def isIndexHidden(self, index):
        """
        Overriden base method that returns True if the specified index is hidden (e.g. a 
        collapsed child in a tree view)

        :param index:   The model index to query if it's hidden
        :returns:       True if the index is hidden, False otherwise
        """
        if not index.isValid():
            return False

        parent_index = index.parent() 
        if parent_index == self.rootIndex():
            # root items are never hidden:
            return False

        if parent_index.parent() != self.rootIndex():
            # grandchildren are always hidden:
            return True

        row = parent_index.row()
        if row < len(self._item_info):
            if self._item_info[row].collapsed:
                # parent is collapsed so item is hidden
                return True

        # default is to show the index:
        return False

    def scrollTo(self, index, scroll_hint=QtGui.QAbstractItemView.EnsureVisible):
        """
        Overriden base method used to scroll to the specified index in the viewport
        (TODO - implement behaviour specific to the scroll hint)

        :param index:       The model index to scroll to
        :param scroll_hint: Hint about how the view should scroll - currently ignored!
        """
        viewport_rect = self.viewport().rect()

        item_rect = self._get_item_rect(index)
        item_rect = item_rect.translated(-self.horizontalOffset(), -self.verticalOffset())

        dx = 0
        if item_rect.left() < viewport_rect.left():
            dx = item_rect.left() - viewport_rect.left()
        elif item_rect.right() > viewport_rect.right():
            dx = min(item_rect.right() - viewport_rect.right(),
                     item_rect.left() - viewport_rect.left())
        if dx != 0:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + dx)

        dy = 0
        if item_rect.top() < viewport_rect.top():
            dy = item_rect.top() - viewport_rect.top()
        elif item_rect.bottom() > viewport_rect.bottom():
            dy = min(item_rect.bottom() - viewport_rect.bottom(),
                     item_rect.top() - viewport_rect.top())
        if dy != 0:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + dy)

        # update the viewport
        self.viewport().update()

    def indexAt(self, point):
        """
        Overriden base method that returns the model index under the specified point in 
        the viewport

        :param point:   The QPoint to find the model index for
        :returns:       The model index for the item under the point or an invalid
                        QModelIndex() if there isn't one.
        """
        if not self.model():
            return QtCore.QModelIndex()

        # convert viewport relative point to global point:
        point = point + QtCore.QPoint(self.horizontalOffset(), self.verticalOffset())

        num_rows = len(self._item_info)
        if num_rows != self.model().rowCount():
            # just in case!
            return QtCore.QModelIndex()

        y_offset = self._border.height()
        for row, item_info in enumerate(self._item_info):

            # get point in local space:
            local_point = point + QtCore.QPoint(0, -y_offset)

            if local_point.y() < item_info.rect.y():
                # point definitely isn't on an item as we'd have found it by now!
                break

            # ok, we'll need an index for this row:
            index = self.model().index(row, 0)

            # check if the point is within this item:
            if item_info.rect.contains(local_point):
                return index 

            # update y-offset:
            y_offset += item_info.rect.height()

            if not item_info.collapsed:
                # now check children:
                local_point = point + QtCore.QPoint(0, -y_offset)
                for child_row, (_, _, child_rect) in enumerate(item_info.child_info):
                    if child_rect.contains(local_point):
                        # found a hit on a child item
                        return self.model().index(child_row, 0, index)

                # update y-offset                
                y_offset += item_info.child_area_rect.height() + self._group_spacing
            else:
                y_offset += self._item_spacing.height()

        # no match so return invalid model index
        return QtCore.QModelIndex()

    def moveCursor(self, cursor_action, keyboard_modifiers):
        """
        Overriden base method that returns the index for the item that the specified 
        cursor action will move to.

        Currently handles up, down, left, right, next and previous actions and only
        moves between leaf items in the view, skipping group items.  This could be
        extended in future to treat groups in the same way the regular tree view works
        (e.g. left/right == collapes/expand).

        :param cursor_action:       The action to use when moving the cursor.
        :param keyboard_modifiers:  Any keyboard modifiers that are currentlt active.
        :returns:                   The QModelIndex of the item the cursor should be
                                    moved to.
        """
        index = self.currentIndex()

        # check that the item info is up-to-date:
        if len(self._item_info) != self.model().rowCount():
            return index

        # get the rows for both the index and the parent index:
        row = index.row()
        parent_index = index.parent()
        if not parent_index.isValid() or parent_index.parent() != self.rootIndex():
            return index
        parent_row = parent_index.row()

        parent_item_info = self._item_info[parent_row]
        if len(parent_item_info.child_info) != self.model().rowCount(parent_index):
            return index

        # find the neighbouring row information based on the direction:
        if (cursor_action == QtGui.QAbstractItemView.MoveLeft
            or cursor_action == QtGui.QAbstractItemView.MovePrevious):
            # move to the left of the current item in the same visual row if possible.  If the
            # cursor is at the start of the row then we do nothing.
            if (row < len(parent_item_info.child_info)
                and parent_item_info.child_info[row][0] == parent_item_info.child_info[row-1][0]):
                # just move left 1
                row -= 1
        elif (cursor_action == QtGui.QAbstractItemView.MoveRight
              or cursor_action == QtGui.QAbstractItemView.MoveNext):
            # move to the right of the current item in the same visual row if possible.  If the
            # cursor is at the end of the row then we do nothing.
            if ((row + 1) < len(self._item_info[parent_row].child_info)
                and parent_item_info.child_info[row][0] == parent_item_info.child_info[row+1][0]):
                # just move right 1:
                row += 1
        elif cursor_action == QtGui.QAbstractItemView.MoveUp:
            # move to the same column in the visible visual row above the current item if possible.  If we
            # are on the top visible row in the view then this will do nothing.
            layout_row, layout_column, _ = parent_item_info.child_info[row]
            if layout_row > 0:
                # move up a row within the same group:
                for ri, (r, c, _) in enumerate(reversed(parent_item_info.child_info[:row])):
                    if r == layout_row-1 and c <= layout_column:
                        row = row-1-ri
                        break
            else:
                # see if we have a visible previous group we can move up to:
                prev_item_info = None
                prev_parent_row = 0
                for ii, info in enumerate(reversed(self._item_info[:parent_row])):
                    if not info.collapsed and info.child_info:
                        # we can move up to this group!
                        prev_item_info = info
                        prev_parent_row = parent_row-1-ii
                        break
                if prev_item_info:
                    # try to move up to the last row of the previous group:
                    for ri, (r, c, _) in enumerate(reversed(prev_item_info.child_info)):
                        if (r == 0 and c <= layout_column) or (r > 0 and c == layout_column):
                            parent_row = prev_parent_row
                            row = len(prev_item_info.child_info)-1-ri
                            break

        elif cursor_action == QtGui.QAbstractItemView.MoveDown:
            # move to the same column in the visible visual row below the current item if possible.  If we
            # are on the bottom visible row in the view then this will do nothing.
            layout_row, layout_column, _ = parent_item_info.child_info[row]
            last_layout_row, last_layout_column, _ = parent_item_info.child_info[-1]
            if layout_row < last_layout_row:
                # move down a row within the same group:
                for ri, (r, c, _) in enumerate(parent_item_info.child_info[row:]):
                    if ((r == last_layout_row and c == min(layout_column, last_layout_column))
                        or r > layout_row and c == layout_column):
                        row = row + ri
                        break
            else:
                # see if we have a visible following group we can move down to:
                next_item_info = None
                next_parent_row = 0
                for ii, info in enumerate(self._item_info[parent_row+1:]):
                    if not info.collapsed and info.child_info:
                        # we can move down to this group!
                        next_item_info = info
                        next_parent_row = parent_row + 1 + ii
                        break
                if next_item_info:
                    last_layout_row, last_layout_column, _ = next_item_info.child_info[-1]
                    # try to move down to the first row of the next group:
                    for ri, (r, c, _) in enumerate(next_item_info.child_info):
                        if ((r == last_layout_row and c == min(layout_column, last_layout_column))
                            or c == layout_column):
                            parent_row = next_parent_row
                            row = ri
                            break

        # build a new index based on the new row and parent row:
        if parent_row >= 0 and parent_row < self.model().rowCount():
            parent_index = self.model().index(parent_row, 0)
            if row >= 0 and row < self.model().rowCount(parent_index):
                index = self.model().index(row, 0, parent_index)

        return index


    def horizontalOffset(self):
        """
        Overriden base method that returns the X offset of the viewport within the ideal 
        sized widget

        :returns:   The current x-offset based on the horizontal scroll bar value
        """
        return self.horizontalScrollBar().value()

    def verticalOffset(self):
        """
        Overriden base method that returns the Y offset of the viewport within the ideal 
        sized widget

        :returns:   The current y-offset based on the vertical scroll bar value
        """
        return self.verticalScrollBar().value()    

    def scrollContentsBy(self, dx, dy):
        """
        Overriden base method used to scroll the viewport by the specified deltas

        :param dx:  The horizontal delta to scroll by
        :param dy:  The vertical delta to scroll by
        """
        self.scrollDirtyRegion(dx, dy)
        self.viewport().scroll(dx, dy)
        self.viewport().update()

    def setSelection(self, selection_rect, flags):
        """
        Overriden base method used to set the selection given the selection rectangle and flags

        :param selection_rect:  The selection rectangle that should be used to select any
                                items contained within
        :param flags:           Flags that define if the items within the selection rectangle
                                should be added to, removed from, etc. the current selection
        """
        # convert viewport relative rect to global rect:
        selection_rect = selection_rect.translated(self.horizontalOffset(), self.verticalOffset())

        # now find which item rectangles intersect this rectangle:
        selection = QtGui.QItemSelection()

        num_rows = len(self._item_info)
        if num_rows != self.model().rowCount():
            # just in case!
            return

        y_offset = self._border.height()
        for row, item_info in enumerate(self._item_info):

            # we only allow selection of child items so we can skip testing the group/top level:
            y_offset += item_info.rect.height()

            if not item_info.collapsed:
                # check to see if the selection rect intersects the child area:
                local_selection_rect = selection_rect.translated(0, -y_offset)

                if local_selection_rect.intersects(item_info.child_area_rect):
                    # we'll need an index for this row:
                    index = self.model().index(row, 0)

                    # need to iterate through and check all child items:
                    top_left = bottom_right = None
                    for child_row, (_, _, child_rect) in enumerate(item_info.child_info):

                        if child_rect.intersects(local_selection_rect):
                            child_index = self.model().index(child_row, 0, index)
                            top_left = top_left or child_index
                            bottom_right = child_index
                        else:
                            if top_left:
                                selection.select(top_left, bottom_right)
                                top_left = bottom_right = None

                    if top_left:
                        selection.select(top_left, bottom_right)
                elif local_selection_rect.bottom() > item_info.child_area_rect.top():
                    # no need to look any further!
                    pass

                # update y-offset
                y_offset += item_info.child_area_rect.height() + self._group_spacing
            else:
                y_offset += self._item_spacing.height()

        # update the selection model:
        self.selectionModel().select(selection, flags)

    def visualRegionForSelection(self, selection):
        """
        Overriden base method that returns the region in the viewport encompasing all the 
        selected items

        :param selection:   The selection to return the region for
        :returns:           A QRegion representing the region containing all the selected items
        """
        viewport_offset = (-self.horizontalOffset(), -self.verticalOffset())        

        region = QtGui.QRegion()
        for index_range in selection:
            for row in range(index_range.top(), index_range.bottom()+1):
                index = self.model().index(row, 0, index_range.parent())
                rect = self._get_item_rect(index)
                rect = rect.translated(viewport_offset[0], viewport_offset[1])
                region += rect
        return region

    def paintEvent(self, event):
        """
        Overriden base method that gets called whenever the view needs repainting.

        :param event:    The QPaintEvent containing information about the event
        """
        if not self.model():
            return

        # make sure item rects are up to date:
        self._update_item_info()

        row_count = self.model().rowCount()
        if row_count != len(self._item_info):
            # this shouldn't ever happen but just incase it does then 
            # we shouldn't paint anything as we'll probably get exceptions!
            bundle = sgtk.platform.current_bundle()
            bundle.log_warning("Unable to paint the Grouped List View as the internal cache is out of sync!")
            return

        # build lookups for the group widgets:
        group_widgets_by_row = {}
        for widget, row in self._group_widget_rows.iteritems():
            if row < row_count:
                group_widgets_by_row[row] = widget
        unused_group_widgets = []
        for widget in self._group_widgets:
            if widget not in group_widgets_by_row.values():
                unused_group_widgets.append(widget)
        next_unused_group_widget_idx = 0
        self._group_widget_rows = {}
        group_widgets_to_resize = []

        # pull out the viewport size and offsets:
        update_rect = event.rect()
        viewport_rect = self.viewport().rect()
        viewport_offset = (-self.horizontalOffset(), -self.verticalOffset())

        # start painting:
        painter = QtGui.QPainter(self.viewport())
        try:
            painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)

            # keep track of the y-offset as we go:
            y_offset = self._border.height()
            for row, item_info in enumerate(self._item_info):

                # get valid model index:
                index = self.model().index(row, 0, self.rootIndex())

                # get the rectangle and translate into the correct relative location:
                rect = item_info.rect.translated(viewport_offset[0], viewport_offset[1] + y_offset)

                # test to see if the rectangle exists within the viewport:
                grp_widget = group_widgets_by_row.get(row)
                if rect.isValid and rect.intersects(viewport_rect):
                    # the group widget is visible:
                    if not grp_widget:
                        if next_unused_group_widget_idx < len(unused_group_widgets):
                            grp_widget = unused_group_widgets[next_unused_group_widget_idx]
                            next_unused_group_widget_idx += 1
                        else:
                            # need to create a new group widget and hook up the signals:
                            if hasattr(self.itemDelegate(), "create_group_widget"):
                                grp_widget = self.itemDelegate().create_group_widget(self.viewport())
                            if grp_widget:
                                self._group_widgets.append(grp_widget)
                                grp_widget.toggle_expanded.connect(self._on_group_expanded_toggled)

                    if grp_widget:
                        if grp_widget.geometry() != rect:
                            # add widget to list to be resized later:
                            group_widgets_to_resize.append((grp_widget, rect))

                        # set up this widget for this index:
                        grp_widget.set_expanded(not item_info.collapsed)
                        grp_widget.set_item(index)
                        grp_widget.show()
                        self._group_widget_rows[grp_widget] = row

                elif grp_widget:
                    # group widget is hidden!
                    unused_group_widgets.append(grp_widget)

                # add the group rectangle height to the y-offset
                y_offset += rect.height()

                if not item_info.collapsed:
                    # draw any children:
                    num_child_rows = self.model().rowCount(index)
                    if len(item_info.child_info) == num_child_rows:
                        # draw all children
                        for child_row, (_, _, child_rect) in enumerate(item_info.child_info):
                            # figure out index and update rect:
                            child_index = self.model().index(child_row, 0, index)

                            child_rect = child_rect.translated(viewport_offset[0], viewport_offset[1] + y_offset)
                            if not child_rect.isValid or not child_rect.intersects(update_rect):
                                # no need to draw!
                                continue

                            # set up the rendering options:
                            # option = self.viewOptions())
                            # (AD) - using self.viewOptions() to get the view style options seems
                            # to return an invalid item in some versions of PySide/PyQt!  I think
                            # it's returning a QtGui.QStyleOptionViewItem even though the 
                            # underlying C++ object is a QtGui.QStyleOptionViewItemV2 or higher.
                            #
                            # This would result in option.rect being corrupt immediately after it
                            # was set below!
                            #
                            # creating the object directly and then using initFrom seems to work
                            # though.
                            option = QtGui.QStyleOptionViewItem()
                            option.initFrom(self)

                            option.rect = child_rect

                            if self.selectionModel().isSelected(child_index):
                                option.state |= QtGui.QStyle.State_Selected
                            if child_index == self.currentIndex():
                                option.state |= QtGui.QStyle.State_HasFocus

                            # draw the widget using the item delegate
                            self.itemDelegate().paint(painter, option, child_index)

                    # update the y-offset to include the child area:
                    y_offset += item_info.child_area_rect.height() + self._group_spacing
                else:
                    y_offset += self._item_spacing.height()

            # hide any group widgets that were not used:
            for w in unused_group_widgets[next_unused_group_widget_idx:]:
                if w.isVisible():
                    w.hide()
        finally:
            painter.end()

        # update geometry for any group widgets that need updating
        # Note, this has to be done after painting has finished otherwise
        # the resize event gets blocked!
        for widget, rect in group_widgets_to_resize:
            widget.setGeometry(rect)

        # call the base implementation:
        QtGui.QAbstractItemView.paintEvent(self, event)

    def _on_group_expanded_toggled(self, expanded):
        """
        Slot that gets signalled whenever a group widget is expanded/collapsed.

        :param expanded:    True if the group widget was expanded, False if it was 
                            collapsed
        """
        # get the row that is being expanded:
        group_widget = self.sender()
        row = self._group_widget_rows.get(group_widget)
        if row == None or row >= len(self._item_info):
            return

        # toggle collapsed state for item:        
        self._item_info[row].collapsed = not expanded
        self._item_info[row].dirty = True
        self._update_some_item_info = True

        # and update the viewport:
        self.viewport().update()

    def updateGeometries(self):
        """
        Overriden base method responsible for updating the horizontal and vertical scroll 
        bars so that they will correctly scroll the view's viewport.
        """
        # calculate the maximum height of all visible items in the model:
        max_height = 0
        for item_info in self._item_info:
            max_height += item_info.rect.height() + self._group_spacing
            if not item_info.collapsed:
                max_height += item_info.child_area_rect.height()

        self.horizontalScrollBar().setSingleStep(30)
        self.horizontalScrollBar().setPageStep(self.viewport().width())
        self.horizontalScrollBar().setRange(0, max(0, self._max_width - self.viewport().width()))

        self.verticalScrollBar().setSingleStep(30) # TODO - make this more intelligent!
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setRange(0, max(0, max_height - self.viewport().height()))

    def _get_item_rect(self, index):
        """
        Return the cached item rectangle for the specified model index.

        :param index:   The model index to find the item rectangle for
        :returns:       A QRect representing the rectangle this index occupies in 
                        the view.  This rectangle is viewport relative.
        """
        # first, get the row for each level of the hierarchy (bottom to top)
        rows = []
        while index.isValid() and index != self.rootIndex():
            rows.append(index.row())
            index = index.parent()

        # find the info for the root item:
        root_row = rows[-1]
        if root_row >= len(self._item_info):
            return QtCore.QRect()
        root_info = self._item_info[root_row]

        # and the Y offset for the start of the root item:
        y_offset = self._border.height()
        for row_info in self._item_info[:root_row]:
            y_offset += row_info.rect.height()
            if not row_info.collapsed:
                y_offset += row_info.child_area_rect.height()
                y_offset += self._group_spacing
            else:
                y_offset += self._item_spacing.height()

        # get the rect for the leaf item:
        rect = QtCore.QRect()
        if len(rows) == 1:
            rect = root_info.rect
        else:
            y_offset += root_info.rect.height()
            child_row = rows[-2]
            if child_row < len(root_info.child_info):
                rect = self._item_info[root_row].child_info[child_row][2]

        # and offset the rect by the Y offset:
        rect = rect.translated(0, y_offset)

        return rect

    def _update_item_info(self):
        """
        Update the cached item info when needed.  This updates the item layout for any items that have
        been 'dirtied' or if the widget size has changed, etc.

        This is typically run immediately before painting.
        """
        # double check that the item-info list is the correct length.  PyQt doesn't
        # seem to call 'rowsAboutToBeRemoved' when a model is cleared so this list can 
        # become out of sync!
        if self.model().rowCount() != len(self._item_info):
            self._update_all_item_info = True

        # check to see if the viewport size has changed:
        viewport_sz = self.viewport().size()
        viewport_resized = False
        if not self.verticalScrollBar().isVisible():
            # to avoid unnecessary resizing, we always calculate the viewport width as if
            # the vertical scroll bar were visible:
            scroll_bar_width = self.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)
            viewport_sz.setWidth(viewport_sz.width() - scroll_bar_width)

        if (viewport_sz != self._prev_viewport_sz):
            # the viewport width has changed so we'll need to update all geometry :(
            viewport_resized = True
            # keep track of the new viewport size for the next time
            self._prev_viewport_sz = viewport_sz 

        if not self._update_some_item_info and not self._update_all_item_info and not viewport_resized:
            # nothing to do!
            return

        #print "%s, %s, %s, %s" % (self._update_all_item_info, self._update_some_item_info, viewport_resized, self._item_info)
        self._update_all_item_info = self._update_all_item_info or viewport_resized

        # if we're updating all item info then may as well clear the existing list:
        if self._update_all_item_info:
            self._item_info = []

        viewport_width = viewport_sz.width()
        max_width = viewport_width - self._border.width()
        base_view_options = self.viewOptions()

        # iterate over root items:
        something_updated = False
        for row in range(self.model().rowCount()):

            # get the item info for this row - create it if needed!
            item_info = None
            if row < len(self._item_info):
                item_info = self._item_info[row]
            else:
                item_info = GroupedListView._ItemInfo()
                self._item_info.append(item_info)

            if not self._update_all_item_info and not item_info.dirty:
                # no need to update item info!
                max_width = max(max_width, item_info.child_area_rect.width())
                continue

            # construct the model index for this row:
            index = self.model().index(row, 0)

            # get the size of the item:
            view_options = base_view_options
            item_size = self.itemDelegate().sizeHint(view_options, index)
            item_info.rect = QtCore.QRect(self._border.width(), 0, item_size.width(), item_size.height())

            # update size info of children:
            row_height = 0
            relative_column = 0
            relative_row = 0
            left = self._border.width()
            x_pos = left
            y_pos = self._item_spacing.height()
            child_info = []
            for child_row in range(self.model().rowCount(index)):
                child_index = self.model().index(child_row, 0, index)

                # do we need to modify the view options?
                view_options = base_view_options

                # get the item size:
                child_item_size = self.itemDelegate().sizeHint(view_options, child_index)

                # see if it fits in the current row:
                if x_pos == left or (x_pos + child_item_size.width()) < viewport_width:
                    # item will fit in the current row!
                    pass
                else:
                    # start a new row for this item:
                    y_pos = y_pos + row_height + self._item_spacing.height()
                    row_height = 0
                    x_pos = left
                    relative_column = 0
                    relative_row += 1

                # store the item rect:
                child_item_rect = QtCore.QRect(x_pos, y_pos, 
                                               child_item_size.width(), 
                                               child_item_size.height())
                child_info.append((relative_row, relative_column, child_item_rect))

                # keep track of the tallest row item:                
                row_height = max(row_height, child_item_rect.height())
                x_pos += self._item_spacing.width() + child_item_rect.width()
                max_width = max(child_item_rect.right(), max_width)
                relative_column += 1

            item_info.child_info = child_info
            item_info.child_area_rect = QtCore.QRect(self._border.width(), 0, max_width, y_pos + row_height)

            # reset dirty flag for item:
            item_info.dirty = False
            something_updated = True

        # reset flags:
        self._update_all_item_info = False
        self._update_some_item_info = False

        if something_updated:
            # update all root level items to be the full width of the viewport:
            for item_info in self._item_info:
                item_info.rect.setRight(max_width)
            self._max_width = max_width

            # update scroll bars for the new dimensions:            
            self.updateGeometries()




