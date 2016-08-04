# Copyright (c) 2016 Shotgun Software Inc.
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

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_model",
)

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_globals",
)

class ShotgunSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    """
    A sort/filter proxy model that handles sorting and filtering
    data in a ShotgunModel by given Shotgun fields on the entities
    stored therein.
    """
    def __init__(self, parent):
        """
        Initializes a new ShotgunSortFilterProxyModel.

        :param parent: The Qt parent of the proxy model.
        """
        super(ShotgunSortFilterProxyModel, self).__init__(parent)

        self._filter_by_fields = ["id"]
        self._sort_by_fields = ["id"]
        self._primary_sort_field = "id"

    ##########################################################################
    # properties

    def _get_filter_by_fields(self):
        """
        A list of string Shotgun field names to filter on.
        """
        return self._filter_by_fields

    def _set_filter_by_fields(self, fields):
        self._filter_by_fields = list(fields)

    filter_by_fields = property(_get_filter_by_fields, _set_filter_by_fields)

    def _get_sort_by_fields(self):
        """
        A list of string Shotgun field names to sort by.
        """
        return self._sort_by_fields

    def _set_sort_by_fields(self, fields):
        self._sort_by_fields = list(fields)

    sort_by_fields = property(_get_sort_by_fields, _set_sort_by_fields)

    def _get_primary_sort_field(self):
        """
        A string Shotgun field name that acts as the primary field to sort on.
        """
        return self._primary_sort_field

    def _set_primary_sort_field(self, field):
        self._primary_sort_field = field

    primary_sort_field = property(_get_primary_sort_field, _set_primary_sort_field)

    ##########################################################################
    # methods

    def lessThan(self, left, right):
        """
        Returns True if "left" is less than "right", otherwise
        False. This sort is handled based on the data pulled from
        Shotgun for the current sort_by_field registered with this
        proxy model.

        :param left:    The QModelIndex of the left-hand item to
                        compare.
        :param right:   The QModelIndex of the right-hand item to
                        compare against.

        :returns:       Whether "left" is less than "right".
        :rtype:         bool
        """
        sg_left = shotgun_model.get_sg_data(left)
        sg_right = shotgun_model.get_sg_data(right)

        if not sg_left or not sg_right:
            return False

        # Sorting by multiple columns, where each column is given a chance
        # to say that the items are out of order. This isn't a stable sort,
        # because we have no way of knowing the current position of left
        # and right in the list, and we have no way to tell Qt that they're
        # equal. That's going to be consistent across Qt, though, so nothing
        # we can/should do about it.
        #
        # We push the primary sort field to the beginning of the list of
        # fields that we're going to sort on, then least the rest in their
        # existing order to act as secondary sort fields.
        secondary_sort_fields = [f for f in self.sort_by_fields if f != self.primary_sort_field]

        # We are also going to shove "id" to the end of the secondary list
        # if it is present. This is because it will never be equal between
        # two entities, and thus will act as a wall to any secondary fields
        # we might want to sort by lower in the list. As such, we'll treat
        # it as the lowest priority.
        if "id" in secondary_sort_fields:
            secondary_sort_fields = [f for f in secondary_sort_fields if f != "id"] + ["id"]

        sort_fields = [self.primary_sort_field] + secondary_sort_fields

        for sort_by_field in sort_fields:
            try:
                left_data = self._get_processable_field_data(
                    sg_left,
                    sort_by_field,
                    sortable=True,
                )
                right_data = self._get_processable_field_data(
                    sg_right,
                    sort_by_field,
                    sortable=True,
                )
            except KeyError:
                # If we got a KeyError, it means that the data we're trying
                # to compare doesn't exist in one item or the other. This would
                # most likely be due to the data not having been queried, and
                # should be an edge case. In this situation, we just can't compare
                # these fields and we need to move on to the rest.
                continue

            if left_data == right_data:
                # If the fields are equal then there's no sorting we need to
                # do based on this field. We'll just continue on to the rest.
                continue
            else:
                return (left_data < right_data)

        return False

    def filterAcceptsRow(self, row, source_parent):
        """
        Returns True if the model index should be shown, and False
        if it should not. This is determined based on whether the
        proxy model's filter is found in the Shotgun data for
        the fields specified in the filter_by_fields list registered
        with the proxy model.

        :param row:             The row being processed.
        :param source_parent:   The parent index from the source model.

        :returns:               Whether the row is accepted.
        :rtype:                 bool
        """
        if not self.filter_by_fields:
            return True

        # We only have one column, so column 0 is what we're
        # after.
        sg_data = shotgun_model.get_sg_data(
            self.sourceModel().index(row, 0, source_parent),
        )

        if not sg_data:
            return True

        for field in self.filter_by_fields:
            try:
                match_data = self._get_processable_field_data(sg_data, field)
            except KeyError:
                continue

            # No support for boolean fields.
            if isinstance(match_data, bool):
                continue

            # We'll make this a looser match by making it case insensitive
            # and bounding it with wildcards. This makes using the search
            # feature much more like a "search" and less like a regex
            # experiment.
            regex = self.filterRegExp()
            regex.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            regex.setPattern("*%s*" % regex.pattern())

            if regex.exactMatch(str(match_data)):
                return True

        return False

    def _get_processable_field_data(self, sg_data, field, sortable=False):
        """
        For a given entity dictionary and field name, returns sortable
        and/or searchable data.

        :param sg_data:     An entity dictionary.
        :param field:       A string Shotgun field to process.
        :param sortable:    If True, sortable data will be returned. If
                            not, data better suited to searching/filtering
                            will be returned. Default is False.

        :returns:           The given Shotgun data in a form that is
                            processable as part of a filtering and/or
                            sorting operation.
        """
        data_type = shotgun_globals.get_data_type(
            self.sourceModel().get_entity_type(),
            field,
        )

        # Certain field data types will need to be treated specially
        # in order to properly search them. Those are handled here,
        # though it's possible additional types will need to be
        # specifically handled. Of the data types listed in the SG
        # Python API at the time of this writing, the below represents
        # those that will not stringify well for this purpose.
        if data_type == "entity":
            processable_data = sg_data[field]["name"]
        elif data_type == "status_list":
            status_name = shotgun_globals.get_status_display_name(sg_data[field])

            # If this isn't needed for sorting, then we just give back
            # the status display name, which is better suited to filtering.
            if not sortable:
                return status_name

            # If we're interested in returning data for sorting, then we
            # will provide an integer value representing the status' order
            # as defined in Shotgun.
            statuses = shotgun_globals.get_ordered_status_list(display_names=True)
            try:
                processable_data = statuses.index(status_name)
            except Exception:
                # This is unlikely to ever be the case unless there's
                # possibly a status cache sync issue, but if it does
                # we can just give it a number less than 0 so that a
                # status that we don't have information on will just
                # end up sorting before the others.
                processable_data = -1
        elif data_type == "multi_entity":
            processable_data = "".join([e.get("name", "") for e in sg_data[field]])
        elif data_type == "date_time":
            if sg_data[field] is not None:
                processable_data = shotgun_globals.create_human_readable_timestamp(
                    sg_data[field],
                    " %I:%M%p",
                )
            else:
                processable_data = ""
        elif data_type == "tag_list":
            processable_data = "".join(sg_data[field])
        else:
            processable_data = sg_data[field]

        return processable_data


