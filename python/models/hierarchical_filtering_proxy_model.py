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
    class _IndexAcceptedCache(object):
        """
        Cached 'accepted' values for indexes.  Uses a dictionary that maps the row hierarchy
        to a tuple containing a QPersistentModelIndex for the index and its accepted value.

        (row, row, row, row) -> (QPersistentModelIndex, accepted)

        When looking up the cached value, the persistent model index is used to ensure that the
        cache entry is still valid (does it match the index we are searching for).

        Note, this deliberately doesn't use a dictionary indexed by QPersistentModelIndexes as
        these are not hashable types in earlier versions of PySide!
        """
        def __init__(self):
            """
            Construction
            """
            self._cache = {}
            self.enabled = True
            self._cache_hits = 0
            self._cache_misses = 0

        @property
        def cache_hit_miss_ratio(self):
            """
            Useful for debug to see how many cache hits vs misses there are
            """
            total_cache_queries = self._cache_hits + self._cache_misses
            if total_cache_queries > 0:
                return float(self._cache_hits) / float(total_cache_queries)
            else:
                return 0
            
        @property
        def size(self):
            """
            Return the current size of the cache
            """
            return len(self._cache)

        def add(self, index, accepted):
            """
            Add the specified index to the cache together with it's accepted state

            :param index:       The QModelIndex to be added
            :param accepted:    True if the model index is accepted by the filtering, False if not.
            """
            if not self.enabled:
                return

            cache_key = self._gen_cache_key(index)
            self._cache[cache_key] = (QtCore.QPersistentModelIndex(index), accepted)

        def remove(self, index):
            """
            Remove the specified index from the cache.

            :param index:   The QModelIndex to remove from the cache
            """
            if not self.enabled:
                return

            cache_key = self._gen_cache_key(index)
            if cache_key in self._cache:
                del self._cache[cache_key]

        def get(self, index):
            """
            Get the accepted state for the specified index in the cache.

            :param index:   The QModelIndex to get the accepted state for
            :returns:       The accepted state if the index was found in the cache, otherwise None
            """
            if not self.enabled:
                return None

            cache_key = self._gen_cache_key(index)
            cache_value = self._cache.get(cache_key)
            if not cache_value:
                self._cache_misses += 1
                return None

            p_index, accepted = cache_value
            if p_index and p_index == index:
                # index and cached value are still valid!
                self._cache_hits += 1
                return accepted
            else:
                # row has changed but accepted value is presumably still valid
                #del self._cache[cache_key]
                #self.add(p_index, accepted)
                self._cache_misses += 1
                return None

        def minimize(self):
            """
            Minimize the size of the cache by removing any entries that are no longer valid
            """
            if not self.enabled:
                return

            self._cache = dict([(k, v) for k, v in self._cache.iteritems() if v[0].isValid()])

        def clear(self):
            """
            Clear the cache
            """
            if not self.enabled:
                return

            self._cache = {}

        def _gen_cache_key(self, index):
            """
            Generate the key for the specified index in the cache.

            :param index:   The QModelIndex to generate a cache key for
            :returns:       The key of the index in the cache
            """
            # ideally we would just use persistent model indexes but these aren't hashable
            # in early versions of PySide :(
            #return QtCore.QPersistentModelIndex(index)

            # the cache key is a tuple of all the row indexes of the parent
            # hierarchy for the index.  First, find the row indexes:
            rows = []
            parent_idx = index
            while parent_idx.isValid():
                rows.append(parent_idx.row())
                parent_idx = parent_idx.parent()

            # return a tuple of the reversed indexes:
            return tuple(reversed(rows))


    def __init__(self, parent=None):
        """
        Construction
        :param parent:    The parent QObject to use for this instance
        """
        QtGui.QSortFilterProxyModel.__init__(self, parent)

        self._filter_dirty = True
        self._accepted_cache = HierarchicalFilteringProxyModel._IndexAcceptedCache()
        self._child_accepted_cache = HierarchicalFilteringProxyModel._IndexAcceptedCache()

    def setFilterRegExp(self, reg_exp):
        """
        """
        self._filter_dirty = True
        QtGui.QSortFilterProxyModel.setFilterRegExp(self, reg_exp)

    def setFilterFixedString(self, pattern):
        """
        """
        self._filter_dirty = True
        QtGui.QSortFilterProxyModel.setFilterFixedString(self, pattern)

    def setFilterCaseSensitivity(self, cs):
        """
        """
        self._filter_dirty = True
        QtGui.QSortFilterProxyModel.setFilterCaseSensitivity(self, cs)

    def setFilterKeyColumn(self, column):
        """
        """
        self._filter_dirty = True
        QtGui.QSortFilterProxyModel.setFilterKeyColumn(self, column)

    def setFilterRole(self, role):
        """
        """
        self._filter_dirty = True
        QtGui.QSortFilterProxyModel.setFilterRole(self, role)

    def enable_caching(self, enable=True):
        """
        Allow control over enabling/disabling of the accepted cache used to accelerate
        filtering.  Can be used for debug purposes to ensure the caching isn't the cause
        of incorrect filtering/sorting or instability!

        :param enable:    True if caching should be enabled, False if it should be disabled. 
        """
        self._accepted_cache.clear()
        self._accepted_cache.enabled = False
        self._child_accepted_cache.clear()
        self._child_accepted_cache.enabled = False

    def _is_row_accepted(self, src_row, src_parent_idx, parent_accepted):
        """
        Override this method to decide if the specified row should be accepted or not by
        the filter.

        This should be overridden instead of filterAcceptsRow in derived classes

        :param src_row:         The row in the source model to filter
        :param src_parent_idx:  The parent QModelIndex instance to filter
        :param parent_accepted: True if a parent item has been accepted by the filter
        :returns:               True if this index should be accepted, otherwise False
        """
        raise NotImplementedError("HierarchicalFilteringProxyModel._is_row_accepted() must be overridden"
                                  " in derived classes!")

    # -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------

    def invalidate(self):
        """
        Overriden base class method used to invalidate sorting and filtering.
        """
        self._filter_dirty = True
        # call through to the base class:
        QtGui.QSortFilterProxyModel.invalidate(self)

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
        if self._filter_dirty:
            #print ("Accepted cache (%d) hits: %d%%" 
            #            % (self._accepted_cache.size, self._accepted_cache.cache_hit_miss_ratio * 100.0))
            #print ("Child accepted cache (%d) hits: %d%%" 
            #            % (self._child_accepted_cache.size, self._child_accepted_cache.cache_hit_miss_ratio * 100.0))

            # clear the cache as the search filter has changed
            self._accepted_cache.clear()
            self._child_accepted_cache.clear()
            self._filter_dirty = False

        # get the source index for the row:
        src_model = self.sourceModel()
        src_idx = src_model.index(src_row, 0, src_parent_idx)

        # first, see if any children of this item are known to already be accepted
        child_accepted = self._child_accepted_cache.get(src_idx)
        if child_accepted == True:
            # child is accepted so this item must also be accepted
            return True

        # next, we need to determine if the parent item has been accepted.  To do this,
        # search up the hierarchy stopping at the first parent that we know for sure if
        # it has been accepted or not.
        upstream_indexes = []
        current_idx = src_idx
        parent_accepted = False
        while current_idx and current_idx.isValid():
            accepted = self._accepted_cache.get(current_idx)
            if accepted != None:
                parent_accepted = accepted
                break
            upstream_indexes.append(current_idx)
            current_idx = current_idx.parent()

        # now update the accepted status for items that we don't know
        # for sure, working from top to bottom in the hierarchy ending
        # on the index we are checking for:
        for idx in reversed(upstream_indexes):
            accepted = self._is_row_accepted(idx.row(), idx.parent(), parent_accepted)
            self._accepted_cache.add(idx, accepted)
            parent_accepted = accepted

        if parent_accepted:
            # the index we are testing was accepted!
            return True
        elif src_model.hasChildren(src_idx):
            # even though the parent wasn't accepted, it may still be needed if one or more
            # children/grandchildren/etc. are accepted:
            return self._is_child_accepted_r(src_idx, parent_accepted)
        else:
            # index wasn't accepted and has no children
            return False  

    def _is_child_accepted_r(self, idx, parent_accepted):
        """
        Recursively check children to see if any of them have been accepted.

        :param idx:             The model index whose children should be checked
        :param parent_accepted: True if a parent item has been accepted
        :returns:               True if a child of the item is accepted by the filter
        """
        model = idx.model()

        # check to see if any children of this item are known to have been accepted:
        child_accepted = self._child_accepted_cache.get(idx)
        if child_accepted != None:
            # we already computed this so just return the result
            return child_accepted

        # need to recursively iterate over children looking for one that is accepted:
        child_accepted = False
        for ci in range(model.rowCount(idx)):
            child_idx = idx.child(ci, 0)

            # check if child item is in cache:
            accepted = self._accepted_cache.get(child_idx)
            if accepted == None:
                # it's not so lets see if it's accepted and add to the cache:
                accepted = self._is_row_accepted(child_idx.row(), idx, parent_accepted)
                self._accepted_cache.add(child_idx, accepted)

            if model.hasChildren(child_idx):
                child_accepted = self._is_child_accepted_r(child_idx, accepted)
            else:
                child_accepted = accepted

            if child_accepted:
                # found a child that was accepted so we can stop searching
                break

        # cache if any children were accepted:
        self._child_accepted_cache.add(idx, child_accepted)
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
            prev_source_model.dataChanged.disconnect(self._on_source_model_data_changed)

        # clear out the various caches:
        self._filter_dirty = True
        self._accepted_cache.clear()
        self._child_accepted_cache.clear()

        # call base implementation:
        QtGui.QSortFilterProxyModel.setSourceModel(self, model)

        # connect to the new model:
        if model:
            model.rowsInserted.connect(self._on_source_model_rows_inserted)
            model.dataChanged.connect(self._on_source_model_data_changed)

    def _on_source_model_data_changed(self, start_idx, end_idx):
        """
        Slot triggered when data for one or more items in the source model changes.

        Data in the source model changing may mean that the filtering for an item changes.  If this
        is the case then we need to make sure we clear the item from the caches.

        :param start_idx:   The index of the first row in the range of model items that have changed
        :param start_idx:   The index of the last row in the range of model items that have changed
        """
        if self.sender() != self.sourceModel():
            return

        parent_idx = start_idx.parent()
        if parent_idx != end_idx.parent():
            # this should never happen but just in case indicate that the entire cache should 
            # be cleared
            self._filter_dirty = True
            return

        # clear all rows from the accepted caches
        for row in range(start_idx.row(), end_idx.row()+1):
            idx = self.sourceModel().index(row, 0, parent_idx)
            self._child_accepted_cache.remove(idx)
            self._accepted_cache.remove(idx)

        # remove parent hierarchy from caches as well:
        while parent_idx.isValid():
            self._child_accepted_cache.remove(parent_idx)
            self._accepted_cache.remove(parent_idx)
            parent_idx = parent_idx.parent()

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
        if self.sender() != self.sourceModel():
            return

        if not parent_idx.isValid():
            return

        accepted = self._accepted_cache.get(parent_idx)
        if accepted == False:
            # the parent item has previously been filtered out but adding new children might
            # change this so lets invalidate everything forcing an update of the proxy model
            self.invalidate()

