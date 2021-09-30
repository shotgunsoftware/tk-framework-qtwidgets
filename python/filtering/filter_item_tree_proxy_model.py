# Copyright (c) 2021 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .filter_item import FilterItem

# from ..models import HierarchicalFilteringProxyModel
models = sgtk.platform.current_bundle().import_module("models")


class FilterItemTreeProxyModel(models.HierarchicalFilteringProxyModel):
    """
    A filter proxy model that filters the source tree model data using a list of
    FilterItem objects. This provides similar functionality as the
    FilterItemFilterProxyModel, except for models that need to inherit from the
    HierarchicalfilteringProxyModel.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """

        super(FilterItemTreeProxyModel, self).__init__(*args, **kwargs)

        # Default to AND all of the filter items upon filtering.
        self._group_op = FilterItem.FilterOp.AND
        # The list of filter items to apply to the model on filtering.
        self._filter_items = []

    @property
    def filter_group_op(self):
        """
        Get or set the operation applied to the list of filter items in this model upon filtering.
        """
        return self._group_op

    @filter_group_op.setter
    def filter_group_op(self, value):
        self._group_op = value

    @property
    def filter_items(self):
        """
        Get or set the filter items used to filter the model data.
        """
        return self._filter_items

    def set_filter_items(self, items, emit_signal=True):
        """
        Set the list of FilterItem objects used to filter the model data. If `emit_signal`, then also
        invalidate the filter to immediately trigger re-filtering the model data.
        """

        self._filter_items = items

        if emit_signal:
            # Invalidate the filter to apply the new filters to the model.
            self.layoutAboutToBeChanged.emit()
            self.invalidateFilter()
            self.layoutChanged.emit()

    def _is_row_accepted(self, src_row, src_parent_idx, parent_accepted):
        """
        Override the base method implementation.

        Return True if the the row is accepted by the filter items. The row is
        accepted if the data is accepted by the list of FilterItems OR'ed or
        AND'ed together, depending on the group operation.

        :param src_row: The row in the source model to filter.
        :type src_row: int
        :param src_parent_idx: The parent index of the source model's row to filter.
        :type src_parent_idx: :class:`sgtk.platform.qt.QModelIndex`
        :param parent_accepted: True if the parent is known already to be accepted, else False.
        :type parent_accepted: bool

        :return: True if the row is accepted, else False.
        :rtype: bool
        """

        # This assume the data to filter on from the source model is alawys the first column.
        src_idx = self.sourceModel().index(src_row, 0, src_parent_idx)

        if not src_idx.isValid():
            return False

        if not self.filter_items:
            return True  # No filters set, accept everything

        return FilterItem.do_filter(src_idx, self.filter_items, self._group_op)
