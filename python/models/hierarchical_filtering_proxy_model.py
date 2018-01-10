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

from collections import deque


class HierarchicalFilteringProxyModel(QtGui.QSortFilterProxyModel):
    """
    Inherited from a :class:`~PySide.QtGui.QSortFilterProxyModel`, this class implements filtering across all 
    levels of a hierarchy in a hierarchical (tree-based) model and provides a simple
    interface for derived classes so that all they need to do is filter a single item
    as requested.
    """
    
    
    class _IndexRejectedCache(object):
        """
        Cached 'rejected' values for indexes.  Uses a dictionary that maps a key to a tuple
        containing a QPersistentModelIndex for the index and its rejected value.

            key -> (QPersistentModelIndex, rejected)

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

        def add(self, index, rejected):
            """
            Add or update the specified index to the cache together with it's
            rejected state.

            :param index:       The QModelIndex to be added or updated.
            :param rejected:    True if the model index is rejected by the filtering,
                                False if not.
            """
            if not self.enabled:
                return

            cache_key = self._gen_cache_key(index)
            p_index = cache_key if self._use_persistent_index_keys else QtCore.QPersistentModelIndex(index)
            self._cache[cache_key] = (p_index, rejected)

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
            Get the rejected state for the specified index in the cache.

            :param index:   The QModelIndex to get the rejected state for.
            :returns:       The rejected state if the index was found in the cache,
                            otherwise None.
            """
            if not self.enabled:
                return None

            cache_key = self._gen_cache_key(index)
            cache_value = self._cache.get(cache_key)
            if not cache_value:
                self._cache_misses += 1
                return None

            p_index, rejected = cache_value
            if p_index and p_index == index:
                # index and cached value are still valid!
                self._cache_hits += 1
                return rejected
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

        self._rejected_cache = HierarchicalFilteringProxyModel._IndexRejectedCache()
        self._refresh_queued = False

    def enable_caching(self, enable=True):
        """
        Allow control over enabling/disabling of the rejected cache used to accelerate
        filtering.  Can be used for debug purposes to ensure the caching isn't the cause
        of incorrect filtering/sorting or instability!

        :param enable:    True if caching should be enabled, False if it should be disabled. 
        """
        # clear the rejected cache - this will make sure we don't use out-of-date
        # information from the cache
        self._clear_rejection_cache()
        self._rejected_cache.enabled = enable

    def _is_row_accepted(self, src_row, src_parent_idx, parent_accepted=False):
        """
        Override this method to decide if the specified row should be accepted or not by
        the filter.

        This should be overridden instead of filterAcceptsRow in derived classes.

        .. note::
            The `parent_accepted` param is kept for backward compatibility but is
            always `False`. This method is never called for an item which has an
            accepted parent.

        :param src_row:         The row in the source model to filter
        :param src_parent_idx:  The parent QModelIndex instance to filter
        :param parent_accepted: Deprecated, always False.
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
        self._clear_rejection_cache()
        QtGui.QSortFilterProxyModel.setFilterRegExp(self, reg_exp)

    def setFilterFixedString(self, pattern):
        """
        Overriden base class method to set the filter fixed string
        """
        self._clear_rejection_cache()
        QtGui.QSortFilterProxyModel.setFilterFixedString(self, pattern)

    def setFilterCaseSensitivity(self, cs):
        """
        Overriden base class method to set the filter case sensitivity
        """
        self._clear_rejection_cache()
        QtGui.QSortFilterProxyModel.setFilterCaseSensitivity(self, cs)

    def setFilterKeyColumn(self, column):
        """
        Overriden base class method to set the filter key column
        """
        self._clear_rejection_cache()
        QtGui.QSortFilterProxyModel.setFilterKeyColumn(self, column)

    def setFilterRole(self, role):
        """
        Overriden base class method to set the filter role
        """
        self._clear_rejection_cache()
        QtGui.QSortFilterProxyModel.setFilterRole(self, role)

    def invalidate(self):
        """
        Overriden base class method used to invalidate sorting and filtering.
        """
        self._clear_rejection_cache()
        # call through to the base class:
        QtGui.QSortFilterProxyModel.invalidate(self)

    def invalidateFilter(self):
        """
        Overriden base class method used to invalidate the current filter.
        """
        self._clear_rejection_cache()
        # call through to the base class:
        QtGui.QSortFilterProxyModel.invalidateFilter(self)

    def filterAcceptsRow(self, src_row, src_parent_idx):
        """
        Overriden base class method used to determine if a row is accepted by the
        current filter.

        This implementation checks the given row and its descendants to decide if
        the item should be accepted or not. It means a whole subtree has to be
        traversed to reject a particular item.

        A rejection cache is build when this method is called on top nodes to
        avoid to compute the same values again and again when this method is called
        in nodes deeper in the hierarchy. This cache keeps track of pruned branches
        in the tree.

        :param src_row:         The row in the source model to filter
        :param src_parent_idx:  The parent index in the source model to filter
        :returns:               True if the row should be accepted by the filter, False
                                otherwise
        """
        # Get the source index for the row:
        src_model = self.sourceModel()
        src_idx = src_model.index(src_row, 0, src_parent_idx)

        # Check if we are dealing with top nodes
        if not src_parent_idx.parent() or not src_parent_idx.parent().isValid():
            self._update_rejection_cache(src_idx)
            # We can now just return the cached value which was may be modified
            # when traversing the tree.
            cached_value = self._rejected_cache.get(src_idx)
            return not cached_value
        else:
            # If we are reaching this level, it means that our parent was accepted.
            # There are two cases:
            # 1) The parent itself was accepted.
            # 2) The parent was accepted because one of its descendants was accepted.
            # For 2) we check if we were rejected when during the top to bottom
            # initial traversal. If we are not in the rejected cache, or we were
            # not rejected, we can be accepted without any further checking.
            cached_value = self._rejected_cache.get(src_idx)
            if cached_value:
                # We were rejected, return that we are not accepted.
                return False
            else:
                # None or False
                # - None means that this depth didn't have to be checked during
                #   the initial traversal.
                # - False means that this depth was reached and was not rejected.
                return True


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
            prev_source_model.rowsRemoved.disconnect(self._on_source_model_rows_removed)
            prev_source_model.dataChanged.disconnect(self._on_source_model_data_changed)
            prev_source_model.modelAboutToBeReset.disconnect(self._on_source_model_about_to_be_reset)

        # clear out the rejection cache:
        self._clear_rejection_cache()

        # call base implementation:
        QtGui.QSortFilterProxyModel.setSourceModel(self, model)

        # connect to the new model:
        if model:
            model.rowsInserted.connect(self._on_source_model_rows_inserted)
            model.rowsRemoved.connect(self._on_source_model_rows_removed)
            model.dataChanged.connect(self._on_source_model_data_changed)
            model.modelAboutToBeReset.connect(self._on_source_model_about_to_be_reset)

    # -------------------------------------------------------------------------------
    # Private methods

    def _update_rejection_cache(self, from_index):
        """
        Update the rejection cache from the given index.

        The cache at the given index has to be cleared before calling this method
        to force a refresh.

        :param from_index: A :class:`QModelIndex` instance.
        """
        if not from_index or not from_index.isValid():
            return
        # Do we have a value from a previous iteration?
        cached_value = self._rejected_cache.get(from_index)
        if cached_value is not None:
            return not cached_value
        # We don't have a cache value check if this item can be accepted
        accepted = self._is_row_accepted(from_index.row(), from_index.parent(), False)
        self._rejected_cache.add(from_index, not accepted)
        if accepted:
            # Great, no need to check further.
            return True
        # We need to check if we should be accepted because one of our
        # descendant is accepted.
        # We keep a list of indexes to check, add new indexes at the end and
        # unqueue them from the left (first in first out).
        descendant_indexes = deque()
        for row_i in range(from_index.model().rowCount(from_index)):
            descendant_indexes.append(from_index.child(row_i, 0))
        while descendant_indexes:
            child_index = descendant_indexes.popleft()
            rejected = self._rejected_cache.get(child_index)
            if cached_value is None:
                # Compute the value
                accepted = self._is_row_accepted(
                    child_index.row(),
                    child_index.parent(),
                    False
                )
                rejected = not accepted
                self._rejected_cache.add(child_index, rejected)
            if rejected:
                # We need to check children, if any, add them in the
                # descendant list.
                for row_i in range(child_index.model().rowCount(child_index)):
                    descendant_indexes.append(child_index.child(row_i, 0))
            else:
                # This item is accepted, no need to check descendants.
                # Go up in the tree and flag the path leading to us as "accepted"
                # By not adding children in the descendant list we stop the
                # traversal at this level.
                # Please note that we might get higher in the tree hierarchy than
                # the depth of our starting index, potentially up to the top nodes.
                parent_index = child_index.parent()
                while parent_index and parent_index.isValid():
                    if self._rejected_cache.get(parent_index) == False:
                        # The path to parent_index is already accepted, no
                        # need to go further up.
                        break
                    self._rejected_cache.add(parent_index, False)
                    parent_index = parent_index.parent()

    def _clear_rejection_cache(self):
        """
        Clear the rejection cache.
        """
        self._rejected_cache.clear()

    def _deferred_refresh(self):
        """
        Run a posted deferred refresh by invalidating the current filter.

        This does not rebuild the rejection cache by just ensure it is applied.
        """
        self._refresh_queued = False
        # Run the base implementation to not invalidate our cache.
        QtGui.QSortFilterProxyModel.invalidateFilter(self)

    def _post_refresh(self):
        """
        Workaround for the rejected cache being updated and the QSortFilterProxyModel
        instance not being aware of it: post a full refresh of the proxy model
        and ensure only one is queued at any time.
        """
        if not self._refresh_queued:
            self._refresh_queued = True
            # With a 0 timeout we're posting an event which will be processed as
            # soon as the Qt event loop becomes idle.
            QtCore.QTimer.singleShot(0, self._deferred_refresh)

    def _on_source_model_data_changed(self, start_idx, end_idx):
        """
        Slot triggered when data for one or more items in the source model changes.

        Data in the source model changing may mean that the filtering for an item
        changes.  If this is the case then we need to make sure we refresh any
        affected entries from the cache.

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
            self._clear_rejection_cache()

        # Get the current value for the parent
        cached_value = self._rejected_cache.get(parent_idx)
        # Clear the cache value for the parent.
        self._rejected_cache.remove(parent_idx)
        # And recompute the cache from it.
        self._update_rejection_cache(parent_idx)
        # Get the new value
        new_cached_value = self._rejected_cache.get(parent_idx)
        # And check if it changed
        if new_cached_value != cached_value:
            # cache changes might have happened for items higher in the tree
            # but the QSortFilterProxyModel will not be aware of them: in the base
            # implementation a node change can't affect something higher in the
            # hierarchy. As a brute force workaround post a full refresh to ensure
            # the proxy model is up to date with the cache.
            self._post_refresh()

    def _on_source_model_rows_inserted(self, parent_idx, start, end):
        """
        Slot triggered when rows are inserted into the source model.

        If new rows are inserted, they might affect a parent item which was
        previously filtered out. So we recompute the cache for the path leading
        to the new rows.

        :param parent_idx:  The index of the parent model item
        :param start:       The first row that was inserted into the source model
        :param end:         The last row that was inserted into the source model
        """
        if (not parent_idx.isValid()
            or parent_idx.model() != self.sourceModel()):
            # invalid input parameters so ignore!
            return

        # Get the current value for the parent
        cached_value = self._rejected_cache.get(parent_idx)
        # Clear the cache value for the parent.
        self._rejected_cache.remove(parent_idx)
        # And recompute the cache from it.
        self._update_rejection_cache(parent_idx)
        # Get the new value
        new_cached_value = self._rejected_cache.get(parent_idx)
        # And check if it changed
        if new_cached_value != cached_value:
            # cache changes might have happened for items higher in the tree
            # but the QSortFilterProxyModel will not be aware of them: in the base
            # implementation a node change can't affect something higher in the
            # hierarchy. As a brute force workaround post a full refresh to ensure
            # the proxy model is up to date with the cache.
            self._post_refresh()

    def _on_source_model_rows_removed(self, parent_idx, start, end):
        """
        Slot triggered when rows are deleted from the source model.

        If rows are deleted, they might affect a parent item which was
        previously accepted. So we invalidate the cache for the path leading
        to the new rows.

        :param parent_idx:  The index of the parent model item
        :param start:       The first row that was inserted into the source model
        :param end:         The last row that was inserted into the source model
        """
        if (not parent_idx.isValid()
            or parent_idx.model() != self.sourceModel()):
            # invalid input parameters so ignore!
            return

        # Get the current value for the parent
        cached_value = self._rejected_cache.get(parent_idx)
        # Clear the cache value for the parent.
        self._rejected_cache.remove(parent_idx)
        # And recompute the cache from it.
        self._update_rejection_cache(parent_idx)
        # Get the new value
        new_cached_value = self._rejected_cache.get(parent_idx)
        # Check if we were accepted and are now rejected
        if new_cached_value == True and not cached_value:
            # The cached value was an explicit (True) or implicit (None) acceptance
            # We need to update the path leading to us to prune it
            up_index = parent_idx.parent()
            proxy_index = None
            while up_index and up_index.isValid():
                proxy_index = self.mapFromSource(up_index)
                if not proxy_index or not proxy_index.isValid():
                    # For an unknown reason the parent source index is not in
                    # the filtered view, let's stop here...
                    break
                # If the parent has a single child it means we were the only
                # reason for the parent to be accepted, which is not the case
                # anymore. Stop here if there is not a single child
                if proxy_index.model().rowCount(proxy_index) != 1:
                    break
                # Reject the parent
                self._rejected_cache.add(up_index, True)
                # And keep going up
                up_index = up_index.parent()
            # cache changes might have happened for items higher in the tree
            # but the QSortFilterProxyModel will not be aware of them: in the base
            # implementation a node change can't affect something higher in the
            # hierarchy. As a brute force workaround post a full refresh to ensure
            # the proxy model is up to date with the cache.
            self._post_refresh()

    def _on_source_model_about_to_be_reset(self):
        """
        Called when the source model is about to be reset.
        """
        # QPersistentModelIndex are constantly being tracked by the owning model so that their references
        # are always valid even after nodes siblings removed. When a model is about to be reset
        # we are guaranteed that the indices won't be valid anymore, so clearning thoses indices now
        # means the source model won't have to keep updating them as the tree is being cleared, thus slowing
        # down the reset.
        self._clear_rejection_cache()
