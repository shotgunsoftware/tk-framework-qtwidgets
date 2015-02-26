# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Proxy model that provides efficient hierarhcical filtering of a tree-based source model
"""

import sgtk
from sgtk.platform.qt import QtCore, QtGui

class HierarchicalFilteringProxyModel(QtGui.QSortFilterProxyModel):
    """
    Inherited from a QSortFilterProxyModel, this class implements filtering across all 
    levels of the hierarchy in a hierarchical (tree-based) model
    """
    
    def __init__(self, parent=None):
        """
        Construction
        :param parent:    The parent QObject to use for this instance
        """
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        
        self._cached_regexp = None
        self._filter_dirty = True
        self._accepted_cache = {}
        self._child_accepted_cache = {}

    def _is_item_accepted(self, item, parent_accepted):
        """
        Override this method to decide if the specified item should be accepted or 
        not by the filter.
        
        This should be overridden instead of filterAcceptsRow in derived classes
        
        :param item:            The QStandardItem item
        :param parent_accepted: True if a parent item has been accepted by the filter
        :returns:               True if this item should be accepted, otherwise False
        """
        raise NotImplementedError()

    # -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------

    def invalidateFilter(self):
        """
        Overriden base class method used to invalidate the current filter.
        """
        self._filter_dirty = True
        # call through to the base class:
        QtGui.QSortFilterProxyModel.invalidateFilter(self)

    def filterAcceptsRow(self, src_row, src_parent_idx):
        """
        Overriden base class method used to determine if a row is accepted by the
        current filter.
        
        This implementation checks both up and down the hierarchy to determine if
        this row should be accepted.

        :param src_row:         The row in the source model to filter
        :param src_parent_idx:  The parent index in the source model to filter
        :returns:               True if the row should be accepted by the filter, False
                                otherwise
        """
        reg_exp = self.filterRegExp()
        if self._filter_dirty or reg_exp != self._cached_regexp:
            # clear the cache as the search filter has changed
            self._accepted_cache = {}
            self._child_accepted_cache = {}
            self._cached_regexp = reg_exp
            self._filter_dirty = False
        
        # get the source index for the row:
        src_model = self.sourceModel()
        src_idx = src_model.index(src_row, 0, src_parent_idx)
        src_item = src_model.itemFromIndex(src_idx)
        
        # first, see if any children of this item are known to already be accepted
        child_accepted = self._child_accepted_cache.get(id(src_item), None)
        if child_accepted == True:
            # child is accepted so this item must also be accepted
            return True

        # next, we need to determine if the parent item has been accepted.  To do this,
        # search up the hierarchy stopping at the first parent that we know for sure if
        # it has been accepted or not.
        upstream_items = []
        current_idx = src_idx
        parent_accepted = False
        while current_idx and current_idx.isValid():
            item = src_model.itemFromIndex(current_idx)
            accepted = self._accepted_cache.get(id(item), None)
            if accepted != None:
                parent_accepted = accepted
                break
            upstream_items.append(item)
            current_idx = current_idx.parent()
            
        # now update the accepted status for items that we don't know
        # for sure:
        for item in reversed(upstream_items):
            accepted = self._is_item_accepted(item, parent_accepted)
            self._accepted_cache[id(item)] = accepted
            parent_accepted = accepted

        if src_item.hasChildren():
            # the parent acceptance doesn't mean that it is filtered out as this
            # depends if there are any children accepted:            
            return self._is_child_accepted_r(src_item, parent_accepted)
        else:
            return parent_accepted  

    def _is_child_accepted_r(self, item, parent_accepted):
        """
        Recursively check children to see if any of them have been accepted.

        :param item:            The item whose children should be checked
        :param parent_accepted: True if a parent item has been accepted
        :returns:               True if a child of the item is accepted by the filter
        """
        # check to see if any children of this item are known to have been accepted:
        child_accepted = self._child_accepted_cache.get(id(item), None)
        if child_accepted != None:
            # we already computed this so just return the result
            return child_accepted
        
        # need to recursively iterate over children looking for one that is accepted:
        child_accepted = False
        for ci in range(item.rowCount()):
            child_item = item.child(ci)
            
            # check if child item is in cache:
            accepted = self._accepted_cache.get(id(child_item), None)
            if accepted == None:
                # it's not so lets see if it's accepted and add to the cache:
                accepted = self._is_item_accepted(child_item, parent_accepted)
                self._accepted_cache[id(child_item)] = accepted

            if child_item.hasChildren():
                child_accepted = self._is_child_accepted_r(child_item, accepted)
            else:
                child_accepted = accepted
                
            if child_accepted:
                # found a child that was accepted so we can stop searching
                break

        # cache if any children were accepted:
        self._child_accepted_cache[id(item)] = child_accepted     
        return child_accepted    
