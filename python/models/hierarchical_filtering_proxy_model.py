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
    Inherited from a :class:`~PySide.QtGui.QSortFilterProxyModel`, this class implements filtering across all 
    levels of a hierarchy in a hierarchical (tree-based) model and provides a simple
    interface for derived classes so that all they need to do is filter a single item
    as requested.
    """
    
    
    class _IndexAcceptedCache(object):
        """
        Cached 'accepted' values for indexes.  Uses a dictionary that maps a key to a tuple 
        containing a QPersistentModelIndex for the index and its accepted value.

            key -> (QPersistentModelIndex, accepted)

        In recent versions of PySide, the key is just a QPersistentModelIndex which has the
        advantage that cache entries don't become invalid when rows are added/moved.

        In older versions of PySide (e.g. in 1.0.9 used by Nuke 6/7/8/9) this isn't possible 
        as QPersistentModelIndex isn't hashable so instead a tuple of the row hierarchy is used 
        and then when looking up the cached value, the persistent model index is used to ensure 
        that the cache entry is still valid.
        """
        def __init__(self):
            """
            Construction
            """
            self._cache = {}
            self.enabled = True
            self._cache_hits = 0
            self._cache_misses = 0

            # ideally we'd use QPersistentModelIndexes to key into the cache but these 
            # aren't hashable in earlier versions of PySide!
            self._use_persistent_index_keys = True
            try:
                # wouldn't it be nice if there were an in-built mechanism to test if a type was
                # hashable!
                hash(QtCore.QPersistentModelIndex())
            except:
                self._use_persistent_index_keys = False

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
            p_index = cache_key if self._use_persistent_index_keys else QtCore.QPersistentModelIndex(index)
            self._cache[cache_key] = (p_index, accepted)

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
                # row has changed so results are bad!
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
            if self._use_persistent_index_keys:
                return QtCore.QPersistentModelIndex(index)

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
        :param parent:    The parent QObject to use for this instance
        :type parent:     :class:`~PySide.QtGui.QWidget`  
        """
        QtGui.QSortFilterProxyModel.__init__(self, parent)

        self._accepted_cache = HierarchicalFilteringProxyModel._IndexAcceptedCache()
        self._child_accepted_cache = HierarchicalFilteringProxyModel._IndexAcceptedCache()

    def enable_caching(self, enable=True):
        """
        Allow control over enabling/disabling of the accepted cache used to accelerate
        filtering.  Can be used for debug purposes to ensure the caching isn't the cause
        of incorrect filtering/sorting or instability!

        :param enable:    True if caching should be enabled, False if it should be disabled. 
        """
        # clear the accepted cache - this will make sure we don't use out-of-date 
        # information from the cache
        self._dirty_all_accepted()
        self._accepted_cache.enabled = enable
        self._child_accepted_cache.enabled = enable

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
    # Overriden base class methods

    def setFilterRegExp(self, reg_exp):
        """
        Overriden base class method to set the filter regular expression
        """
        self._dirty_all_accepted()
        QtGui.QSortFilterProxyModel.setFilterRegExp(self, reg_exp)

    def setFilterFixedString(self, pattern):
        """
        Overriden base class method to set the filter fixed string
        """
        self._dirty_all_accepted()
        QtGui.QSortFilterProxyModel.setFilterFixedString(self, pattern)

    def setFilterCaseSensitivity(self, cs):
        """
        Overriden base class method to set the filter case sensitivity
        """
        self._dirty_all_accepted()
        QtGui.QSortFilterProxyModel.setFilterCaseSensitivity(self, cs)

    def setFilterKeyColumn(self, column):
        """
        Overriden base class method to set the filter key column
        """
        self._dirty_all_accepted()
        QtGui.QSortFilterProxyModel.setFilterKeyColumn(self, column)

    def setFilterRole(self, role):
        """
        Overriden base class method to set the filter role
        """
        self._dirty_all_accepted()
        QtGui.QSortFilterProxyModel.setFilterRole(self, role)

    def invalidate(self):
        """
        Overriden base class method used to invalidate sorting and filtering.
        """
        self._dirty_all_accepted()
        # call through to the base class:
        QtGui.QSortFilterProxyModel.invalidate(self)

    def invalidateFilter(self):
        """
        Overriden base class method used to invalidate the current filter.
        """
        self._dirty_all_accepted()
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
            prev_source_model.modelAboutToBeReset.disconnect(self._on_source_model_about_to_be_reset)

        # clear out the various caches:
        self._dirty_all_accepted()

        # call base implementation:
        QtGui.QSortFilterProxyModel.setSourceModel(self, model)

        # connect to the new model:
        if model:
            model.rowsInserted.connect(self._on_source_model_rows_inserted)
            model.dataChanged.connect(self._on_source_model_data_changed)
            model.modelAboutToBeReset.connect(self._on_source_model_about_to_be_reset)

    # -------------------------------------------------------------------------------
    # Private methods

    def _is_child_accepted_r(self, idx, parent_accepted):
        """
        Recursively check children to see if any of them have been accepted.

        :param idx:             The model index whose children should be checked
        :param parent_accepted: True if a parent item has been accepted
        :returns:               True if a child of the item is accepted by the filter
        """
        model = idx.model()

        # check to see if any children of this item are known to have been accepted:
        cached_value = self._child_accepted_cache.get(idx)
        if cached_value is not None:
            # we already computed this so just return the result
            return cached_value

        # need to recursively iterate over children looking for one that is accepted:
        child_accepted = False
        for ci in range(model.rowCount(idx)):
            child_idx = idx.child(ci, 0)

            # Check if child item is in cache:
            child_accepted = self._accepted_cache.get(child_idx)
            if child_accepted is None:
                # It's not in the cache so lets see if it's accepted and add to the cache:
                child_accepted = self._is_row_accepted(child_idx.row(), idx, parent_accepted)
                self._accepted_cache.add(child_idx, child_accepted)

            if not child_accepted and model.hasChildren(child_idx):
                # This child was not accepted.
                # Recurse down and check if any grand children are accepted.
                child_accepted = self._is_child_accepted_r(child_idx, False)

            if child_accepted:
                # This child node or one of its descendants indicated that they
                # were accepted so exit early.
                break

        # Cache if one of the descendants was accepted or not.
        self._child_accepted_cache.add(idx, child_accepted)
        return child_accepted

    def _dirty_all_accepted(self):
        """
        Dirty/clear the accepted caches
        """
        self._accepted_cache.clear()
        self._child_accepted_cache.clear()

    def _dirty_accepted_rows(self, parent_idx, start, end):
        """
        Dirty the specified rows from the accepted caches.  This will remove any entries in
        either the accepted or the child accepted cache that match the start/end rows for the
        specified parent index.

        This also dirties the parent hierarchy to ensure that any filtering is re-calculated for
        those parent items.

        :param parent_idx:  The parent model index to dirty rows for
        :param start:       The first row in to dirty
        :param end:         The last row to dirty
        """
        # clear all rows from the accepted caches
        for row in range(start, end+1):
            idx = self.sourceModel().index(row, 0, parent_idx)
            self._child_accepted_cache.remove(idx)
            self._accepted_cache.remove(idx)

        # remove parent hierarchy from caches as well:
        while parent_idx.isValid():
            self._child_accepted_cache.remove(parent_idx)
            self._accepted_cache.remove(parent_idx)
            parent_idx = parent_idx.parent()

    def _on_source_model_data_changed(self, start_idx, end_idx):
        """
        Slot triggered when data for one or more items in the source model changes.

        Data in the source model changing may mean that the filtering for an item changes.  If this
        is the case then we need to make sure we clear any affected entries from the cache

        :param start_idx:   The index of the first row in the range of model items that have changed
        :param start_idx:   The index of the last row in the range of model items that have changed
        """
        if (not start_idx.isValid() or not end_idx.isValid()
            or start_idx.model() != self.sourceModel() 
            or end_idx.model() != self.sourceModel()):
            # invalid input parameters so ignore!
            return

        parent_idx = start_idx.parent()
        if parent_idx != end_idx.parent():
            # this should never happen but just in case, dirty the entire cache:
            self._dirty_all_accepted()

        # dirty specific rows in the caches:
        self._dirty_accepted_rows(parent_idx, start_idx.row(), end_idx.row())

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
        if (not parent_idx.isValid()
            or parent_idx.model() != self.sourceModel()):
            # invalid input parameters so ignore!
            return

        # dirty specific rows in the caches:
        self._dirty_accepted_rows(parent_idx, start, end)

    def _on_source_model_about_to_be_reset(self):
        """
        Called when the source model is about to be reset.
        """
        # QPersistentModelIndex are constantly being tracked by the owning model so that their references
        # are always valid even after nodes siblings removed. When a model is about to be reset
        # we are guaranteed that the indices won't be valid anymore, so clearning thoses indices now
        # means the source model won't have to keep updating them as the tree is being cleared, thus slowing
        # down the reset.
        self._dirty_all_accepted()
