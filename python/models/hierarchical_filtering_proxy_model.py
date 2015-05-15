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
import weakref
    
import sgtk
from sgtk.platform.qt import QtCore, QtGui

class HierarchicalFilteringProxyModel(QtGui.QSortFilterProxyModel):
    """
    Inherited from a QSortFilterProxyModel, this class implements filtering across all 
    levels of the hierarchy in a hierarchical (tree-based) model
    """
    
    # The caches used to optimise filtering use weak refs which will outlive the items
    # they reference and would lead to an ever-growing cache if not cleaned.  This
    # value determines how often the caches should be cleaned/trimmed of invalid refs.
    _MAX_FILTERS_BEFORE_CACHE_CLEAN = 256
    
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
        
        self._filter_count = 0

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
            self._filter_count = 0
        elif self._filter_count > HierarchicalFilteringProxyModel._MAX_FILTERS_BEFORE_CACHE_CLEAN:
            # clear out any invalid weak refs from the cache
            # to ensure it doesn't grow insanely big!
            new_cache = {}
            for k, v in self._accepted_cache.iteritems():
                if k() is not None:
                    new_cache[k] = v
            self._accepted_cache = new_cache
            new_cache = {}
            for k, v in self._child_accepted_cache.iteritems():
                if k() is not None:
                    new_cache[k] = v
            self._child_accepted_cache = new_cache
            self._filter_count = 0
        self._filter_count += 1
        
        # get the source index for the row:
        src_model = self.sourceModel()
        src_idx = src_model.index(src_row, 0, src_parent_idx)
        src_item = src_model.itemFromIndex(src_idx)
        
        # first, see if any children of this item are known to already be accepted
        child_accepted = self._child_accepted_cache.get(weakref.ref(src_item))
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
            accepted = self._accepted_cache.get(weakref.ref(item))
            if accepted != None:
                parent_accepted = accepted
                break
            upstream_items.append(item)
            current_idx = current_idx.parent()
            
        # now update the accepted status for items that we don't know
        # for sure:
        for item in reversed(upstream_items):
            accepted = self._is_item_accepted(item, parent_accepted)
            self._accepted_cache[weakref.ref(item)] = accepted
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
        child_accepted = self._child_accepted_cache.get(weakref.ref(item))
        if child_accepted != None:
            # we already computed this so just return the result
            return child_accepted
        
        # need to recursively iterate over children looking for one that is accepted:
        child_accepted = False
        for ci in range(item.rowCount()):
            child_item = item.child(ci)
            
            # check if child item is in cache:
            accepted = self._accepted_cache.get(weakref.ref(child_item))
            if accepted == None:
                # it's not so lets see if it's accepted and add to the cache:
                accepted = self._is_item_accepted(child_item, parent_accepted)
                self._accepted_cache[weakref.ref(child_item)] = accepted

            if child_item.hasChildren():
                child_accepted = self._is_child_accepted_r(child_item, accepted)
            else:
                child_accepted = accepted
                
            if child_accepted:
                # found a child that was accepted so we can stop searching
                break

        # cache if any children were accepted:
        self._child_accepted_cache[weakref.ref(item)] = child_accepted
        return child_accepted    

    def setSourceModel(self, model):
        """
        Overridden base method that we use to keep track of when rows are inserted into the 
        source model

        :param model:   The source model to track
        """
        # if needed, disconnect from the previous source model:
        prev_source_model = self.sourceModel()
        if prev_source_model:
            prev_source_model.rowsInserted.disconnect(self._on_source_model_rows_inserted)

        # call base implementation:
        QtGui.QSortFilterProxyModel.setSourceModel(self, model)

        # connect to the new model:
        if model:
            model.rowsInserted.connect(self._on_source_model_rows_inserted)

    def _on_source_model_rows_inserted(self, parent_idx, start, end):
        """
        Slot triggered when rows are inserted into the source model.

        There appears to be a limitation with the QSortFilterProxyModel that breaks sorting
        of newly added child rows when the parent row has previously been filtered out.  This
        can happen when the model data is lazy-loaded as the filtering may decide that as
        there are no valid children, then the parent should be filtered out.  However, when
        matching children later get added, the parent then matches but the children don't get
        sorted correctly!

        The workaround is to detect when children are added to a parent that was previously
        filtered out and force the whole proxy model to be invalidated (so that the filtering
        and sorting are both applied from scratch).

        The alternative would be to implement our own version of the QSortFilterProxyModel!

        :param parent_idx:  The index of the parent model item
        :param start:       The first row that was inserted into the source model
        :param end:         The last row that was inserted into the source model
        """
        if not parent_idx.isValid():
            return

        parent_item = self.sourceModel().itemFromIndex(parent_idx)
        if not parent_item:
            return

        accepted = self._accepted_cache.get(weakref.ref(parent_item))
        if accepted == False:
            # the parent item has previously been filtered out but adding new children might
            # change this so lets invalidate everything forcing an update of the proxy model
            self.invalidate()

