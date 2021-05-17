# Copyright (c) 2021 Shotgun Software Inc.
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

# from .framework_qtwidgets import HierarchicalFilteringProxyModel
from ..models import HierarchicalFilteringProxyModel
from .filter_item import FilterItem


class TreeProxyModel(HierarchicalFilteringProxyModel):
    """
    A proxy model for source models with a tree data structure.

    TODO: rename to just FilterProxyModel ?
    TODO: Move this to tk-frameowrk-qtwidgets once the model is more fleshed out.
    """

    def __init__(self, *args, **kwargs):
        """
        TreeProxyModel constructor
        """

        # HierarchicalFilteringProxyModel.__init__(self, parent)
        super(TreeProxyModel, self).__init__(*args, **kwargs)

        # self._filter_items = filter_items
        self._filter_items = []

    @property
    def filter_items(self):
        """
        Get or set the filter items used to filter the model data.
        """
        return self._filter_items

    @filter_items.setter
    def filter_items(self, items):
        self._filter_items = items
        self.invalidateFilter()

    def _is_row_accepted(self, src_row, src_parent_idx, parent_accepted):
        """
        Override the base method.

        Go through the list of filters and check whether or not the src_row
        is accepted based on the filters.
        """

        src_idx = self.sourceModel().index(src_row, 0, src_parent_idx)
        if not src_idx.isValid():
            return False

        # FIXME comment out for now for Task model which is a list, not tree model? but it says its a tree model?
        # if not src_parent_idx.isValid():
        # return True  # Accept all group headers for now

        if not self.filter_items:
            return True  # No filters set, accept everything

        return self._do_filter(src_idx, self.filter_items, FilterItem.OP_AND)

    def _do_filter(self, src_idx, filter_items, op):
        """
        Recursively filter the data for the given src_idx.
        """

        if not FilterItem.is_group_op(op):
            raise ValueError("Invalid filter group operation {}".format(op))

        for filter_item in filter_items:
            if filter_item.is_group():
                if not filter_item.filters:
                    # Just accept empty groups
                    accepted = True
                else:
                    accepted = self._do_filter(
                        src_idx, filter_item.filters, filter_item.filter_op
                    )
            else:
                accepted = filter_item.accepts(src_idx)

            if op == FilterItem.OP_AND and not accepted:
                return False

            if op == FilterItem.OP_OR and accepted:
                return True

        if op == FilterItem.OP_AND:
            # Accept if the operation is AND since it would have been rejected immediately if
            # any filter item did not accept it.
            return True

        # Do not accept if the operation is OR (or invalid) since the value would have
        # been accepted immediately if any filters accepted it.
        return False
