# Copyright (c) 2021 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import datetime
import numbers

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from tank_vendor import six

from .filter_item import FilterItem

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals"
)


class FilterDefinition(object):
    """
    A class object that defines a defintion for a set of filters that are determined by model data.

    The definition is built by going through each item in the model. For each item, the data for
    each of the `filter_roles` defined is extracted from the item, and that data is further
    processed to create a filter definition for that item's data. The data is processed based on the
    type of data:

        dictionary:
            A filter item is added for each of the key-value pairs. The field id for these filter
            items will be the "role.field", where the 'field' is one of the dictionary keys. The
            filter id for these filter items will be the "field_id.value", where the 'value' is the
            string representation of the filter value.
        object:
            A filter item is added for each of the object's defined properties. The field id for
            these filter items will be the "role.field", where the 'field' is one of the object
            property names. The filter id for these filter items will be the "field_id.value", where
            the 'value' is the string representation of the filter value.
        SG data:
            A filter item is added for each of the SG field-value pairs. The field id for these filter
            items will be the "sg_entity_type.field", where the 'sg_entity_type' is the entity type for
            the sg data and the'field' is one of the sg data dictionary keys. The filter id for these
            filter items will be the "field_id.value", where the 'value' is the string representation
            of the filter value.

        primitive data:
            One filter item is added for the primitive data. The field id for these filter items will
            be "role.None". Primitive data is not "grouped" so the field (group) is "None". The filter
            id for these filter items will be the "field_id.value", where the 'value' is the string
            representation of the filter value.

    Example of a resulting filter definition:
        {
            "field_1": {
                "name": The display name for the filter field,
                "type": The data type for this filter field,
                "values": {
                    "value_1": {
                        "name": The display name for this filter field value,
                        "value": The actual value for this filter field value,
                        "count": The number of items in the model that have this value,
                        "icon": The icon to display for this filter field value,
                    }
                },
                "data_func": A function that takes parameters: index, role, field. This
                             function is used to get the data from the index used to
                             perform the necessary comparison for filtering.
            },
            "field_2": { ... },
            "field_3": { ... },
            ...
        }

    The keys of the definition are the unique identifier for the field (or group) of filters. The keys of
    the inner "values" dict are the filter ids.
    """

    def __init__(self):
        """Constructor."""

        # The filters definitions that are built based on the current model data, and which are used
        # to build the filter menu UI.
        self._definition = {}

        self._proxy_model = None
        self._filter_roles = [QtCore.Qt.DisplayRole]
        self._accept_fields = set()
        self._ignore_fields = set()
        self._use_fully_qualified_name = True

        # A default SG project to fall back to if the data itself does not specify its project.
        self.__default_sg_project_id = None

        # This is a work around for tree models with deferred loading - filters will be built based
        # on the leaf nodes of tree models, but for deferred loading models, the leaf nodes are not
        # guaranteed to be loaded in the model at time of building the filters.
        self._tree_level = None

    @property
    def filter_roles(self):
        """
        Get or set the filter roles that are used to extract data from the model that drives the
        filter definition.
        """
        return self._filter_roles

    @filter_roles.setter
    def filter_roles(self, value):
        self._filter_roles = value

    @property
    def accept_fields(self):
        """
        Get or set the set of fields that are accepted when building the filter definition.

        Set the value of this property to the empty set if the filter should accept all
        given fields (e.g. it does not ignore any fields).
        """
        return self._accept_fields

    @accept_fields.setter
    def accept_fields(self, value):
        if isinstance(value, list):
            self._accept_fields = set(value)
        else:
            self._accept_fields = value

    @property
    def ignore_fields(self):
        """Get or set the set of fields that will be ignored when building the filter definition."""
        return self._ignore_fields

    @ignore_fields.setter
    def ignore_fields(self, value):
        if isinstance(value, list):
            self._ignore_fields = set(value)
        else:
            self._ignore_fields = value

    @property
    def use_fully_qualified_name(self):
        """
        Get or set whether or not the fully qualified name will be displayed for filter items. This applies to
        SG data, the entity type will be displayed with the entity field name; e.g. Task Id.
        """
        return self._use_fully_qualified_name

    @use_fully_qualified_name.setter
    def use_fully_qualified_name(self, value):
        self._use_fully_qualified_name = value

    @property
    def default_sg_project_id(self):
        """
        Get or set the project id. This will be used to retrive SG specific data, e.g. fields for a given
        entity type.
        """
        return self.__default_sg_project_id

    @default_sg_project_id.setter
    def default_sg_project_id(self, value):
        self.__default_sg_project_id = value

    @property
    def tree_level(self):
        """Get or set the data level within the (tree) model, which the filters are built from."""
        return self._tree_level

    @tree_level.setter
    def tree_level(self, value):
        self._tree_level = value

    @property
    def proxy_model(self):
        """Get or set the proxy model that drives the filter definition."""
        return self._proxy_model

    @proxy_model.setter
    def proxy_model(self, value):
        self._proxy_model = value

    @staticmethod
    def get_index_data(index, role, field):
        """
        Return the data for the given index, role and data field. The field could correspond to
        the index data's object property attribute, dictionary field or irrelevant.
        """

        index_data = index.data(role)
        if not index_data:
            return index_data

        if isinstance(field, six.string_types):
            # First check if the field corresponds to a property on the index data object
            if hasattr(index_data, field):
                return getattr(index_data, field)

            # Next check if the field corresponds to a dictionary field
            if isinstance(index_data, dict):
                return index_data.get(field)

        return index_data

    #############################################@##################################################
    # Public methods
    #############################################@##################################################

    def is_empty(self):
        """Return True if the current filter definition is empty."""

        return not self._definition

    def get_fields(self, sort=False, reverse=False):
        """
        Return the fields for this filter definition.

        :param sort: True will return the fields in sorted order.
        :type sort: bool
        :param reverse: Only takes effect if sort is True. True will return fields in descending
                        order, else ascending.
        :type reverse: bool
        :return: The fields in the definition.
        :rtype: list<str>
        """

        if sort:
            return sorted(
                self._definition,
                key=lambda k: self._definition[k]["name"],
                reverse=reverse,
            )

        return self._definition.keys()

    def get_field_data(self, field_id):
        """
        Return the definition data for the specific field.

        :param field_id: The id of the field.
        :type field_id: str

        :return: The data for the field.
        :rtype: dict
        """

        return self._definition.get(field_id)

    def get_filter_data(self, field_id, value_id):
        """
        Return the data for the specified filter.

        :param field_id: The filter field group id that the filter is in.
        :type field_id: str
        :param value_id: The filter value id to get the data for.
        :type value_id: str

        :return: The filter data. None is returned if the filter does not exist.
        :rtype: dict
        """

        return self._definition.get(field_id, {}).get("values", {}).get(value_id)

    def set_filter_data(self, field_id, value_id, filter_data):
        """
        Set the filter data for the filter.

        :param field_id: The filter field group id that the filter is in.
        :type field_id: str
        :param value_id: The id of the filter value to set the data for.
        :type value_id: str
        :param filter_data: The filter data to set.
        :type filter_data: dict
        """

        if field_id not in self._definition:
            return

        self._definition[field_id].setdefault("values", {})[value_id] = filter_data

    def set_default_value(self, field_id, value_id=None, default_value=None):
        """
        Set the default value for the filter.

        :param field_id: The filter field group id that the filter is in.
        :type field_id: str
        :param value_id: The id of the filter value to set the data for.
        :type value_id: str
        :param default_value: The filter data to set.
        :type default_value: str | dict
        """

        if value_id is None:
            # Set the default value for the filter field group.
            field_data = self.get_field_data(field_id)
            if field_data:
                field_data["default_value"] = default_value
        else:
            # Set the default value for the specific filter.
            filter_data = self.get_filter_data(field_id, value_id)
            if filter_data:
                filter_data["default_value"] = default_value

    def has_filter(self, field_id, value_id):
        """
        Return True if the definition has data for the given filter.

        :param field_id: The id of the filter field group.
        :type value_id: The id of the filter value.

        :return: True if the filter id is in the definition, else False.
        :rtype:bool
        """

        return value_id in self._definition.get(field_id, {}).get("values", {})

    def get_source_model(self):
        """
        Return the source model that drives the filter definition. The source model is source model
        of the proxy model that is defined for the class. If no proxy model is set, the source
        model will be None.

        :return: The source mdoel of the `proxy_model`. If the proxy is not defined, then None.
        :rtype: :class:`sgtk.platform.qt.QtGui.QAbstractItemModel`
        """

        if self.proxy_model:
            return self.proxy_model.sourceModel()

        return None

    def clear(self):
        """Clear the definition."""

        self._definition = {}

    @sgtk.LogManager.log_timing
    def build(self, groups_only=False):
        """Build the filter definition based on the model data."""

        # Clear the existing filters definitions before rebuilding it.
        self.clear()

        # Recursively go through each model item to extract the data to built the filters.
        self.__build_filters(QtCore.QModelIndex(), groups_only=groups_only)

    @sgtk.LogManager.log_timing
    def update_filters(self, field_ids):
        """
        Update only the given filters.

        This update operation will traverse the model data to calculate the current data
        counts for each of the given filters.

        Use this method to update only the required filters, instead of building the whole
        filter definition which can an expensive operation.

        :param field_ids: The filter group field ids of the filters to update.
        :type field_ids: List[str]
        """

        update_ids = []

        for field_id in field_ids:
            if field_id not in self._definition:
                continue

            # Add this filter to the list to update.
            update_ids.append(field_id)

            # Reset filter counts, these will be rebuilt.
            filter_values = self._definition[field_id].get("values", {})
            for value_id in filter_values:
                filter_values[value_id]["count"] = 0

        # Rebuild the specified filters.
        self.__build_filters_by_id(update_ids)

        # Remove any filters that have become empty.
        for field_id in update_ids:
            self._definition[field_id]["values"] = {
                value_id: filter_data
                for value_id, filter_data in self._definition[field_id][
                    "values"
                ].items()
                if filter_data.get("count", 0) > 0
            }

    ###############################################################################################
    # Private methods
    ###############################################################################################

    def __get_field_id(self, role, field, sg_entity_type=None):
        """
        Return the id for the filter field defined by the given data.

        :param role: The model item data role used to retrieve data for this filter field.
        :type role: QtCore.Qt.ItemDataRole
        :param field: The filter field unique name.
        :type field: str
        :param sg_entity_type: (option) If the field represent a ShotGrid data field, then
            the entity type for the field is passed.
        :type sg_entity_field: str

        :return: The filter field id.
        :rtype: str
        """

        if sg_entity_type:
            return "{role}.{sg_entity_type}.{sg_field}".format(
                role=role, sg_entity_type=sg_entity_type, sg_field=field
            )

        return "{role}.{field}".format(role=role, field=field)

    def __process_field_id(self, field_id):
        """
        Process the filter field id and get the SG specific data from it.

        If the `field_id` represents an SG filter, it will have the format:
            {model_item_data_role}.{sg_entity_type}.{sg_field}

        :param field_id: The filter field id that may contain SG data.
        :type field_id: str

        :return: A tuple containing the data for this filter id.
        :rtype: tuple<int, str, str>
        """

        filter_role = None
        sg_entity_type = None
        sg_field = None
        field = None

        try:
            end_of_role_index = field_id.index(".")
        except ValueError:
            return (filter_role, sg_entity_type, sg_field, field)

        try:
            filter_role = int(field_id[:end_of_role_index])
        except ValueError:
            # Not a valid filter id. Must be prefixed with Qt.ItemDataRole.
            return (filter_role, sg_entity_type, sg_field, field)

        # Check if we have SG data. This could be a SG model or it could be a non-SG model but
        # contains SG data.
        field = field_id[end_of_role_index + 1 :]

        try:
            sg_field_index = field.index(".")
        except ValueError:
            return (filter_role, sg_entity_type, sg_field, field)

        sg_entity_type = field[:sg_field_index]
        sg_field = field[sg_field_index + 1 :]
        return (filter_role, sg_entity_type, sg_field, field)

    def __is_accepted(self, field_id, index):
        """
        Return True if the filter field is accepted for the given index.

        :param field_id: The filter field to check acceptance for.
        :type field_id: str
        :param index: The index to get the data to check acceptance with.
        :type index: QtCore.QModelIndex
        """

        if field_id in self.ignore_fields:
            return False

        if self.accept_fields and field_id not in self.accept_fields:
            return False

        return self._filters_accept_index(index, field_id)

    def __build_filters(self, root_index, level=0, groups_only=False):
        """
        Build the filters definition by starting at the given root index, and recursing through all
        child indexes. For each index traversed, the object's internal `_definition` member will be
        modified to include the filter created based off the index data. After all indexes are
        traversed, the `_definition` object will contain the whole set of filters for the model
        data, starting at the given `root_index`.

        :param root_index: The root index to build the filters definition from.
        :type root_index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param level: The level that the root_index is within the model (e.g this is mostly for tree
                      models, for list models all indexes will have level 0).
        """

        source_model = self.get_source_model()
        if not source_model:
            return

        for row in range(source_model.rowCount(root_index)):
            index = source_model.index(row, 0, root_index)

            if not self._proxy_filter_accepts_row(index):
                # Early out. Do not update filters with index data that is not accepted by
                # the proxy model.
                continue

            # Filters are only added for leaf nodes (for list models, this will be all nodes). In
            # the event that the model defers loading its data, the `tree_level` property can be
            # defined to indicate which level of the model tree that the leaf nodes are expected
            # to be on (e.g. ShotgunDeferredEntityModel).
            if (self.tree_level and level == self.tree_level) or (
                not self.tree_level and source_model.rowCount(index) <= 0
            ):
                # A filter will be added for each index and for each filter role defined.
                for role in self.filter_roles:
                    self.__add_filter_from_index(index, role)

            if groups_only and self.accept_fields:
                # We only care to build filter definition such that we have the groupings. Individual filters
                # will be updated once they are visible/active.
                # We can only do this if we know what filters we want though, e.g. accepted filter are defined.
                if len(self._definition) == len(
                    self.accept_fields.difference(self.ignore_fields)
                ):
                    # We found them all.
                    return

            self.__build_filters(index, level + 1)

    def __build_filters_by_id(
        self, field_ids, root_index=QtCore.QModelIndex(), level=0
    ):
        """Recurse through model data to update the filters for the given ids."""

        source_model = self.get_source_model()
        if not source_model:
            return

        for row in range(source_model.rowCount(root_index)):
            index = source_model.index(row, 0, root_index)

            if not self._proxy_filter_accepts_row(index):
                # Early out. Do not update filters with index data that is not accepted by
                # the proxy model.
                continue

            # Filters are only added for leaf nodes (for list models, this will be all nodes). In
            # the event that the model defers loading its data, the `tree_level` property can be
            # defined to indicate which level of the model tree that the leaf nodes are expected
            # to be on (e.g. ShotgunDeferredEntityModel).
            if (self.tree_level and level == self.tree_level) or (
                not self.tree_level and source_model.rowCount(index) <= 0
            ):
                for field_id in field_ids:
                    self.__add_filter_by_id(field_id, index)

            self.__build_filters_by_id(field_ids, index, level + 1)

    def __add_filter_from_index(self, index, role):
        """
        Add a filter for the index and role. Get the data from the index with the given role
        and create a filter definition from the data.

        :param index: The index to add the filter for.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param role: The model item data role to extract data from the index.
        :type role: :class:`sgtk.platform.qt.QtCore.ItemDataRole`
        """

        index_data = index.data(role)
        if not index_data:
            return

        # Check if we have SG data. This could be a SG model or it could be a non-SG model but
        # contains SG data.
        sg_project_id, sg_entity_type = self._get_sg_project_and_entity_type(index_data)

        if sg_entity_type:
            # SG data
            self.__add_filters_from_sg_data(
                sg_entity_type, index_data, sg_project_id, index, role
            )

        elif isinstance(index_data, dict):
            for field, data in index_data.items():
                self.__add_filter_from_data(field, index, role, data)

        elif isinstance(
            index_data,
            (bool, datetime.date, datetime.datetime, six.string_types, numbers.Number),
        ):
            # Primitive data
            field = None
            self.__add_filter_from_data(field, index, role, index_data)

        elif isinstance(index_data, list):
            assert False, "List data type not handled yet"

        else:
            # Object data, extract the data from its object properties
            for field, value in vars(index_data.__class__).items():
                if not isinstance(value, property):
                    continue

                data = getattr(index_data, field)
                self.__add_filter_from_data(field, index, role, data)

    def __add_filter_from_data(self, field, index, role, data):
        """
        Add a filter from the given data.

        :param field: The field (group) the data belongs to.
        :type field: str
        :param data: The data value for the filter.
        :type data: any
        :param index: The index which the filter corresponds to, and which the data
                      was extracted from.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param role: The role that was used to extract the data from the index.
        :type role: :class:`sgtk.platform.qt.QtCore.ItemDataRole`
        """

        if data is None:
            return

        data_type = FilterItem.get_data_type(data)
        if not data_type:
            return

        field_id = self.__get_field_id(role, field)
        if not self.__is_accepted(field_id, index):
            return

        if field is None:
            field_display = "Display"
        else:
            field_display = str(field).title().replace("_", " ")

        self.__add_filter_definition(
            field_id, field, field_display, data_type, data, role
        )

    def __add_filters_from_sg_data(self, entity_type, sg_data, project_id, index, role):
        """
        Add filters from the SG data. Iterate through the SG dictionary data, and
        add a filter for each dict entry.

        :param entity_type: The SG entity type for this sg_data
        :type entity_type: str
        :param sg_data: The SG data to create the filter from.
        :type sg_data: dict
        :param project_id: The SG project id for this sg_data
        :type project_id: int
        :param index: the index which the filter corresponds to.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param role: The role used to extract the data from the index.
        :type role: :class:`sgtk.platform.qt.QtCore.ItemDataRole`
        """

        if self.accept_fields:
            filter_field_ids = self.accept_fields.difference(self.ignore_fields)
        else:
            filter_field_ids = None

        # For better performance, iterate over the smaller data set (only the accepted fields
        # or all of the SG data).
        if filter_field_ids and len(filter_field_ids) < len(sg_data):
            for field_id in filter_field_ids:
                role, entity_type, sg_field, _ = self.__process_field_id(field_id)

                # Check that the field id is valid for this sg data.
                if (
                    entity_type is None
                    or sg_field is None
                    or entity_type != sg_data.get("type")
                ):
                    continue

                data = sg_data.get(sg_field)
                self.__add_filter_from_sg_data(
                    entity_type, sg_field, project_id, data, index, role
                )
        else:
            for sg_field, data in sg_data.items():
                self.__add_filter_from_sg_data(
                    entity_type, sg_field, project_id, data, index, role
                )

    def __add_filter_from_sg_data(
        self, entity_type, sg_field, project_id, value, index, role
    ):
        """
        Add filter from SG data.

        :param project_id: The SG project id for this sg_data
        :type project_id: int
        """

        if value is None:
            return

        try:
            sg_data_type = shotgun_globals.get_data_type(
                entity_type, sg_field, project_id
            )
        except ValueError:
            # Could not find the schema for entity type and field
            return

        # Map the SG data type to a FilterItem type
        data_type = FilterItem.map_from_sg_data_type(sg_data_type)
        if not data_type:
            return

        field_id = self.__get_field_id(role, sg_field, entity_type)
        if not self.__is_accepted(field_id, index):
            return

        field_display = shotgun_globals.get_field_display_name(
            entity_type, sg_field, project_id
        )
        # Save the short field display name, since the field display may be updated to use the
        # longer fully qualified name (including entity display name)
        short_display = field_display

        # Get the entity display name for this data
        entity_display = shotgun_globals.get_type_display_name(entity_type, project_id)

        if self.use_fully_qualified_name:
            # Construct display for deeply linked fields - grab every other item
            # after splitting on the "dot", these will be the deep linked entity
            # types, which we want to display.
            deep_links = sg_field.split(".")[:-1:2]
            if deep_links:
                formatted_deep_links = " ".join(
                    (link.replace("_", " ").title() for link in deep_links)
                )
                if not field_display.startswith(formatted_deep_links):
                    field_display = "{} {}".format(formatted_deep_links, field_display)

            if not field_display.startswith(entity_display):
                field_display = "{entity} {field}".format(
                    entity=entity_display, field=field_display
                )
            else:
                field_display = "{entity_and_field} ({field})".format(
                    entity_and_field=field_display, field=sg_field
                )

        self.__add_filter_definition(
            field_id,
            sg_field,
            field_display,
            data_type,
            value,
            role,
            short_display=short_display,
        )

    def __add_filter_by_id(self, field_id, index):
        """Update the filter from the index data."""

        # Extract the data for the filter from its id.
        role, sg_entity_type, sg_field, field = self.__process_field_id(field_id)
        if role is None:
            return

        index_data = index.data(role)
        if not index_data:
            # No data to update filter with.
            return

        if sg_entity_type:
            # This index has SG data dict.
            if sg_field not in index_data:
                # No SG data to update filter with.
                return

            # Get the project id for this sg data and sanity check the entity type matches.
            project_id, entity_type = self._get_sg_project_and_entity_type(index_data)
            if entity_type != sg_entity_type:
                return

            value = index_data[sg_field]
            self.__add_filter_from_sg_data(
                sg_entity_type, sg_field, project_id, value, index, role
            )
        else:
            # Extract the desired filter field data from the index data.
            if isinstance(index_data, dict):
                data = index_data.get(field)
            elif isinstance(
                index_data,
                (
                    bool,
                    datetime.date,
                    datetime.datetime,
                    six.string_types,
                    numbers.Number,
                ),
            ):
                data = index_data
            elif isinstance(index_data, list):
                # TODO Support List data type
                data = None
            else:
                # Object data, extract the data from its object properties
                try:
                    data = getattr(index_data, field)
                except:
                    data = None

            self.__add_filter_from_data(field, index, role, data)

    def __add_filter_definition(
        self, field_id, field, field_display, data_type, value, role, short_display=None
    ):
        """
        Based on the provided data, create a new filter definition and add it to the internal
        object's `_definition` member.

        :param field_id: The unique id for the field (group) that the filter belongs to.
        :type field_id: str
        :param field: The field this filter belongs to. This may be the property name or dictionary
                      key that the filter data has been derived from.
        :type field: str
        :param field_display: The display (user friendly) value for the filter field.
        :type field_display: str
        :param data_type: The type of data for the filter.
        :type data_type: str
        :param value: The filter data value
        :type value: any
        :param role: The model item data role that this filter data was derived from.
        :type role: :class:`sgtk.platform.qt.QtCore.ItemDataRole`
        :param short_display: Optional value to use as a short display name.
        :type short_display: str
        """

        if isinstance(value, list):
            if not value:
                value.append(None)
            values_list = value
        else:
            values_list = [value]

        for val in values_list:

            if isinstance(val, dict):
                # FIXME this is hard coded to use the "name" key - let this be configurable per data type
                value_id = val.get("name", str(val))
                filter_value = val
                icon_path = val.get("icon", None)
                icon = QtGui.QIcon(icon_path) if icon_path else None
            elif data_type == FilterItem.FilterType.DATETIME:
                datetime_bucket = FilterItem.get_datetime_bucket(value)
                value_id = datetime_bucket
                filter_value = datetime_bucket
                icon_path = None
                icon = None
            else:
                value_id = val
                filter_value = val
                icon_path = None
                icon = None

            # Ensure the value "key" is hashable, since it will be used as a dictionary key
            value_name = str(value_id)
            value_id = "{}.{}".format(field_id, value_name)

            if field_id in self._definition:
                # The filter field (group) already exists, add this filter to the values list.
                self._definition[field_id]["values"].setdefault(
                    value_id, {}
                ).setdefault("count", 0)
                self._definition[field_id]["values"][value_id]["count"] += 1
                self._definition[field_id]["values"][value_id]["name"] = value_name
                self._definition[field_id]["values"][value_id]["value"] = filter_value
                self._definition[field_id]["values"][value_id]["icon_path"] = icon_path
                self._definition[field_id]["values"][value_id]["icon"] = icon
            else:
                # Create a new entry for this filter field (group)
                self._definition[field_id] = {
                    "name": field_display,
                    "short_name": short_display or field_display,
                    "type": data_type,
                    "values": {
                        value_id: {
                            "name": value_name,
                            "value": filter_value,
                            "count": 1,
                            "icon_path": icon_path,
                            "icon": icon,
                        }
                    },
                    "data_func": lambda i, r=role, f=field: self.get_index_data(
                        i, r, f
                    ),
                }

    def _proxy_filter_accepts_row(self, index):
        """
        Return True if the proxy filter model accepts this index row.

        :param index: The index to check acceptance on.
        :type index: :class:`sgkt.platform.qt.QtCore.QModelIndex`
        :return: True if accepted, else False
        :rtype: bool
        """

        return self._proxy_model.filterAcceptsRow(index.row(), index.parent())

    def _filters_accept_index(self, index, field_id):
        """
        Return True if the index associated with the field is accepted.

        Default implementation always returns True. Override this method to provide custom logic
        to accept a given index. For an example, see the FilterMenuFiltersDefinition implementation.

        :param index: The model index to check acceptance on.
        :type index: :class:`sgkt.platform.qt.QtCore.QModelIndex`
        :param field_id: The filter field (group) associated with the index, that may affect the
                         index's acceptance.
        :type field_id: str

        :return: True if the index is accepted, else False
        :rtype: bool
        """

        return True

    def _get_sg_project_and_entity_type(self, sg_data):
        """
        Return the SG entity type and fields associated with the given data, if the data represents
        SG data.

        :param sg_data: The dat to get the entity type from.
        :type sg_data: dict
        :return: The SG entity type, or None if the data is not valid SG data.
        :rtype: str
        """

        if not isinstance(sg_data, dict):
            return (None, None)

        entity_type = sg_data.get("type")
        project_id = sg_data.get("project", {}).get("id") or self.default_sg_project_id

        # Sanity check that this is valid SG entity
        if shotgun_globals.is_valid_entity_type(entity_type, project_id):
            return (project_id, entity_type)

        # Last attempt to extract an entity type for the data - our source model may be a SG model which has an
        # instance method to get the entity type for the model data.
        try:
            source_model = self.get_source_model()
            return (project_id, source_model.get_entity_type())
        except AttributeError:
            return (None, None)


class FilterMenuFiltersDefinition(FilterDefinition):
    """
    Subclass of the FilterDefinition class that is designed specifically to work with the
    FilterMenu class. The filters set from the FilterMenu are used to help determine if indexes
    are accepted or not.

    This subclass assumes the `_proxy_model` is a, or subclass of, the FilterItemProxyModel
    or FilterItemTreeProxyModel class.
    """

    def __init__(self, filter_menu):
        """
        Constructor.
        """

        super(FilterMenuFiltersDefinition, self).__init__()

        # The FilterMenu assoicated with this FilterDefinition.
        self._filter_menu = filter_menu

        # Reset the current menu filters lookup map to ensure the filters reflect the
        # current state of the filter menu. This mapping is used to optimize the
        # _filters_accept_index method.
        self.__current_menu_filters_by_field = {}

    def clear(self):
        """Override the base method."""

        super(FilterMenuFiltersDefinition, self).clear()
        self.__current_menu_filters_by_field = {}

    def update_filters(self, field_ids):
        """Override the base method."""

        self.__current_menu_filters_by_field = {}
        super(FilterMenuFiltersDefinition, self).update_filters(field_ids)

    def _proxy_filter_accepts_row(self, index):
        """
        Return True if the proxy filter model accepts this index row.

        The FilterItem objects defined in the FilterItem[Tree]ProxyModel are disabled when checking
        acceptance. This is to allow the FilterMenu to show filter groups where values from the filter
        group are OR'd together. Further acceptance checking will be done in `_filters_accept_index`.

        :param index: The model index to check acceptance on.
        :type index: :class:`sgkt.platform.qt.QtCore.QModelIndex`
        :return: True if the index is accepted, else False
        :rtype: bool
        """

        # Sanity check for debugging
        assert hasattr(self._proxy_model, "filter_items"), "Invalid proxy model"
        assert hasattr(self._proxy_model, "set_filter_items"), "Invalid proxy model"

        # Temporarily disable the filters, so that when the index is checked against the proxy model
        # for acceptance, that the filtrs defined from this menu are not applied. This is because
        # there may be other filters applied outside of this menu, and we only want to check those
        # filters for acceptance.
        current_filters = self._proxy_model.filter_items
        self._proxy_model.set_filter_items([], emit_signal=False)
        try:
            accepted = self._proxy_model.filterAcceptsRow(index.row(), index.parent())
        finally:
            self._proxy_model.set_filter_items(current_filters, emit_signal=False)

        return accepted

    def _filters_accept_index(self, index, field_id):
        """
        Return True if the index associated with the field is accepted.

        This acceptance is almost the same as `_proxy_filter_accepts_row`, except for it omits
        any filters from the given field. This is to allow the FilterMenu to show filter groups
        where values from the filter group are OR'd together.

        :param index: The model index to check acceptance on.
        :type index: :class:`sgkt.platform.qt.QtCore.QModelIndex`
        :param field_id: Filters that belong to the field_id group are ignored when checking
                         acceptance.
        :type field_id: str
        :return: True if the index is accepted, else False
        :rtype: bool
        """

        if field_id in self.__current_menu_filters_by_field:
            filters = self.__current_menu_filters_by_field.get(field_id)
        else:
            filters = self._filter_menu.get_current_filters(
                exclude_choices_from_fields=[field_id]
            )
            self.__current_menu_filters_by_field[field_id] = filters

        if filters:
            if not FilterItem.do_filter(index, filters):
                return False

        return True
