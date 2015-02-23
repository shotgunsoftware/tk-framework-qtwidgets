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
    """
    class _ItemInfo(object):
        def __init__(self):
            self.rect = QtCore.QRect()              # relative item rect for group header
            self.dirty = True                       # True if data in group or children has changed
            self.collapsed = False                  # True if the group is currently collapsed
            self.child_rects = []                   # List of sizes for all child items relative to the group
            self.child_area_rect = QtCore.QRect()   # total size of child area
    
    def __init__(self, parent=None):
        """
        Construction
        """
        QtGui.QAbstractItemView.__init__(self, parent)
        
        self._item_info = []
        self._update_all_item_info = True
        self._update_some_item_info = False
        self._max_width = 0

        # default the item delegate to the base implementation.  This can
        # be overriden in client code with another delegate derived from
        # GroupedListViewItemDelegate
        self.setItemDelegate(GroupedListViewItemDelegate(self))

        self._group_widgets = []
        self._group_widget_rows = {}
        
        self._prev_viewport_sz = QtCore.QSize()

        self._border = QtCore.QSize(6,6)
        self._group_spacing = 30
        self._item_spacing = QtCore.QSize(4,4)

    def setItemDelegate(self, delegate):
        """
        """
        if not isinstance(delegate, GroupedListViewItemDelegate):
            raise Exception("Item delegate for this view must be derived from 'GroupedListViewItemDelegate'!")
        QtGui.QAbstractItemView.setItemDelegate(self, delegate)

    @property
    def border(self):
        return self._border
    
    @border.setter
    def border(self, border_sz):
        self._border = border_sz
        self._update_all_item_info = True
        self.viewport().update()

    @property
    def group_spacing(self):
        return self._group_spacing
    
    @group_spacing.setter
    def group_spacing(self, spacing):
        self._group_spacing = spacing
        self._update_all_item_info = True
        self.viewport().update()
        
    @property
    def item_spacing(self):
        return self._item_spacing
    
    @item_spacing.setter
    def item_spacing(self, spacing):
        self._item_spacing = spacing
        self._update_all_item_info = True
        self.viewport().update()        
        
    def edit(self, idx, trigger, event):
        """
        """
        if idx.parent() == self.rootIndex():
            # we don't want to allow the regular editing of groups
            # needs to be driven by role though!
            return False
        return QtGui.QAbstractItemView.edit(self, idx, trigger, event)
        
    def set_expanded(self, index, expand):
        """
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
    
    def is_expanded(self, index):
        """
        """
        if not index.isValid() or index.parent() != self.rootIndex():
            return False

        row = index.row()
        if row < len(self._item_info):
            return not self._item_info[row].collapsed
        else:
            return False

        
    def setModel(self, model):
        """
        Set the model the view will use
        """
        self._update_all_item_info = True
        QtGui.QAbstractItemView.setModel(self, model)
        
    def dataChanged(self, top_left, bottom_right):
        """
        Called when data in the model has been changed
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
            # the same parent!
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
        Called when rows have been inserted into the model
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
                # something went wrong!
                self._update_all_item_info = True
                    
        # make sure we schedule a viewport update so that everything gets updated correctly!
        self.viewport().update()
        QtGui.QAbstractItemView.rowsInserted(self, parent_index, start, end)
        
    def rowsAboutToBeRemoved(self, parent_index, start, end):
        """
        Called just before rows are going to be removed from the model
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

        # make sure we schedule a viewport update so that everything gets updated correctly!
        QtGui.QAbstractItemView.rowsAboutToBeRemoved(self, parent_index, start, end)        

        self.viewport().update()
        
    def visualRect(self, index):
        """
        Return the rectangle occupied by the item for the given 
        index in the viewport
        """
        rect = QtCore.QRect()
        if index.isValid():
            rect = self._get_item_rect(index)
            rect = rect.translated(-self.horizontalOffset(), -self.verticalOffset())
        return rect
    
    def isIndexHidden(self, index):
        """
        Return true if the specified index is hidden (e.g. a collapsed child
        in a tree view)
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
    
    def scrollTo(self, index, scroll_hint):
        """
        Scroll to the specified index in the viewport
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
                         
        self.viewport().update()        
        
    def indexAt(self, point):
        """
        Return the index for the specified point in the viewport
        """
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
                for child_row, child_rect in enumerate(item_info.child_rects):
                    if child_rect.contains(local_point):
                        # found a hit on a child item
                        return self.model().index(child_row, 0, index)

                # update y-offset                
                y_offset += item_info.child_area_rect.height() + self._group_spacing
            else:
                y_offset += self._item_spacing.height()
        
        # no match so return model index
        return QtCore.QModelIndex()

    def moveCursor(self, cursor_action, keyboard_modifiers):
        """
        Return the index for the item that the specified cursor action will 
        move to
        """
        index = self.currentIndex()
        # ...
        return index
    
    def horizontalOffset(self):
        """
        Return the X offset of the viewport within the ideal sized widget
        """
        return self.horizontalScrollBar().value()
    
    def verticalOffset(self):
        """
        Return the Y offset of the viewport within the ideal sized widget
        """
        return self.verticalScrollBar().value()    

    def scrollContentsBy(self, dx, dy):
        """
        Scroll the viewport by the specified deltas
        """
        self.scrollDirtyRegion(dx, dy)
        self.viewport().scroll(dx, dy)
        self.viewport().update()

    def resizeEvent(self, event):
        """
        """
        # at the moment, recalculating the dimensions is handled at the start of painting so
        # we don't need to do anything here.  If this causes problems later then we may have
        # to rethink things!
        QtGui.QAbstractItemView.resizeEvent(self, event)

    def setSelection(self, selection_rect, flags):
        """
        Set the selection given the selection rectangle and flags
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
                    for child_row, child_rect in enumerate(item_info.child_rects):
                        
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
        Return the region in the viewport encompasing all the selected items
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
        """
        # make sure item rects are up to date:
        self._update_item_info()

        row_count = self.model().rowCount()
        if row_count != len(self._item_info):
            # this shouldn't ever happen but just incase it does then 
            # we shouldn't paint anything as it'll probably be wrong!
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
                    if len(item_info.child_rects) == num_child_rows:
                        # draw all children
                        for child_row, child_rect in enumerate(item_info.child_rects):
                            # figure out index and update rect:
                            child_index = self.model().index(child_row, 0, index)
                            
                            child_rect = child_rect.translated(viewport_offset[0], viewport_offset[1] + y_offset)
                            if not child_rect.isValid or not child_rect.intersects(update_rect):
                                # no need to draw!
                                continue
                             
                            # set up the rendering options:
                            option = self.viewOptions()
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
        
        self.verticalScrollBar().setSingleStep(30)#00)# TODO - make this more intelligent!
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setRange(0, max(0, max_height - self.viewport().height()))

    def _get_item_rect(self, index):
        """
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
            if child_row < len(root_info.child_rects):
                rect = self._item_info[root_row].child_rects[child_row]

        # and offset the rect by the Y offset:
        rect = rect.translated(0, y_offset)
        
        return rect
            
    def _update_item_info(self):
        """
        """
        # check to see if the viewport size has changed:
        viewport_sz = self.viewport().size()
        viewport_resized = False
        if not self.verticalScrollBar().isVisible():
            # to avoid unnecessary resizing, we always calculate the viewport width as if
            # the vertical scroll bar were visible:
            scroll_bar_width = self.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)
            viewport_sz.setWidth(viewport_sz.width() - scroll_bar_width)

        if viewport_sz != self._prev_viewport_sz:
            # the viewport width has changed so we'll need to update all geometry :(
            viewport_resized = True
            # keep track of the new viewport size for the next time
            self._prev_viewport_sz = viewport_sz 
        
        if not self._update_some_item_info and not self._update_all_item_info and not viewport_resized:
            # nothing to do!
            return
        
        #print "%s, %s, %s, %s" % (self._update_all_item_info, self._update_some_item_info, viewport_resized, self._item_info)
        self._update_all_item_info = self._update_all_item_info or viewport_resized
        
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
            left = self._border.width()
            x_pos = left
            y_pos = self._item_spacing.height()
            child_rects = []  
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

                # store the item rect:
                child_item_rect = QtCore.QRect(x_pos, y_pos, 
                                               child_item_size.width(), 
                                               child_item_size.height())
                child_rects.append(child_item_rect)

                # keep track of the tallest row item:                
                row_height = max(row_height, child_item_rect.height())
                x_pos += self._item_spacing.width() + child_item_rect.width()
                max_width = max(child_item_rect.right(), max_width)

            item_info.child_rects = child_rects
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
        
        

    
    