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
from tank.util import sgre
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
        """
        Constructor.
        """

        # The filters definitions that are built based on the current model data, and which are used
        # to build the filter menu UI.
        self._definition = {}

        self._proxy_model = None
        self._filter_roles = [QtCore.Qt.DisplayRole]
        self._accept_fields = []
        self._ignore_fields = []
        self._use_fully_qualified_name = True
        self._project_id = None
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
        Get or set the fields that will are accepted when building the filter definition.

        Set the value of this property None or the empty list if the filter should accept all
        given fields (e.g. it does not ignore any fields).
        """
        return self._accept_fields

    @accept_fields.setter
    def accept_fields(self, value):
        self._accept_fields = value

    @property
    def ignore_fields(self):
        """
        Get or set the fields that will be ignored when building the filter definition.
        """
        return self._ignore_fields

    @ignore_fields.setter
    def ignore_fields(self, value):
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
    def project_id(self):
        """
        Get or set the project id. This will be used to retrive SG specific data, e.g. fields for a given
        entity type.
        """
        return self._project_id

    @project_id.setter
    def project_id(self, value):
        self._project_id = value

    @property
    def tree_level(self):
        """
        Get or set the data level within the (tree) model, which the filters are built from.
        """
        return self._tree_level

    @tree_level.setter
    def tree_level(self, value):
        self._tree_level = value

    @property
    def proxy_model(self):
        """
        Get or set the proxy model that drives the filter definition.
        """
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

        return self._definition.get(field_id, {})

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
        """
        Clear the definition.
        """

        self._definition = {}

    @sgtk.LogManager.log_timing
    def build(self):
        """
        Return the filters based on the model data.
        """

        # Clear the existing filters definitions before rebuilding it.
        self.clear()

        # Recursively go through each model item to extract the data to built the filters.
        self._build_from_root(QtCore.QModelIndex())

    #############################################@##################################################
    # Protected methods
    #############################################@##################################################

    def _build_from_root(self, root_index, level=0):
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
                # Early out
                # No need to add filters for indexes that are not accepted by the proxy model.
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
                    self._add_filter_from_index(index, role)

            self._build_from_root(index, level + 1)

    def _add_filter_from_index(self, index, role):
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
        sg_entity_type = self._get_sg_entity_type(index_data)

        if sg_entity_type:
            # SG data
            self._add_filters_from_sg_data(index_data, sg_entity_type, index, role)

        elif isinstance(index_data, dict):
            for key, value in index_data.items():
                self._add_filter_from_data(key, value, index, role)

        elif isinstance(
            index_data,
            (bool, datetime.date, datetime.datetime, six.string_types, numbers.Number),
        ):
            # Primitive data
            self._add_filter_from_data(None, index_data, index, role)

        elif isinstance(index_data, list):
            assert False, "List data type not handled yet"

        else:
            # Object data, extract the data from its object properties
            for property_name, value in vars(index_data.__class__).items():
                if not isinstance(value, property):
                    continue

                property_value = getattr(index_data, property_name)
                self._add_filter_from_data(property_name, property_value, index, role)

    def _add_filter_from_data(self, field, data, index, role):
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

        field_id = "{role}.{field}".format(role=role, field=field)
        if field_id in self.ignore_fields or (
            self.accept_fields and field_id not in self.accept_fields
        ):
            return

        data_type = FilterItem.get_data_type(data)
        if not data_type:
            return

        if field is None:
            field_display = "Display"
        else:
            field_display = str(field).title().replace("_", " ")

        if not self._filters_accept_index(index, field_id):
            # Do not add filters for index data that is not accepted
            return

        self._add_filter_definition(
            field_id, field, field_display, data_type, data, role
        )

    def _add_filters_from_sg_data(self, sg_data, entity_type, index, role):
        """
        Add filters from the SG data. Iterate through the SG dictionary data, and
        add a filter for each dict entry.

        :param sg_data: The SG data to create the filter from.
        :type value: dict
        :param index: the index which the filter corresponds to.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param role: The role used to extract the data from the index.
        :type role: :class:`sgtk.platform.qt.QtCore.ItemDataRole`
        :param entity_type: The SG entity type for this sg_data
        :type entity_type: str
        """

        entity_display = shotgun_globals.get_type_display_name(
            entity_type, self.project_id
        )

        for sg_field, value in sg_data.items():
            field_id = "{type}.{field}".format(type=entity_type, field=sg_field)
            if field_id in self.ignore_fields or (
                self.accept_fields and field_id not in self.accept_fields
            ):
                continue

            try:
                data_type = shotgun_globals.get_data_type(
                    entity_type, sg_field, self.project_id
                )
            except ValueError:
                # Could not find the schema for entity type and field
                continue

            # Map the SG data type to a FilterItem type
            data_type = FilterItem.FilterType.MAP_TYPES.get(data_type)
            if not data_type:
                continue

            if not self._filters_accept_index(index, field_id):
                # Do not add filters for index data that is not accepted
                continue

            field_display = shotgun_globals.get_field_display_name(
                entity_type, sg_field, self.project_id
            )

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
                        field_display = "{} {}".format(
                            formatted_deep_links, field_display
                        )

                if not field_display.startswith(entity_display):
                    field_display = "{entity} {field}".format(
                        entity=entity_display, field=field_display
                    )
                else:
                    field_display = "{entity_and_field} ({field})".format(
                        entity_and_field=field_display, field=sg_field
                    )

            self._add_filter_definition(
                field_id, sg_field, field_display, data_type, value, role
            )

    def _add_filter_definition(
        self, field_id, field, field_display, data_type, value, role
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
        """

        if isinstance(value, list):
            if not value:
                value.append(None)
            values_list = value
        else:
            values_list = [value]

        for val in values_list:
            icon = None

            if isinstance(val, dict):
                # FIXME this is hard coded to use the "name" key - let this be configurable per data type
                value_id = val.get("name", str(val))
                filter_value = val
                icon = QtGui.QIcon(val.get("icon", None))
            elif data_type == FilterItem.FilterType.DATETIME:
                datetime_bucket = FilterItem.get_datetime_bucket(value)
                value_id = datetime_bucket
                filter_value = datetime_bucket
            else:
                value_id = val
                filter_value = val

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
                self._definition[field_id]["values"][value_id]["icon"] = icon
            else:
                # Create a new entry for this filter field (group)
                self._definition[field_id] = {
                    "name": field_display,
                    "type": data_type,
                    "values": {
                        value_id: {
                            "name": value_name,
                            "value": filter_value,
                            "count": 1,
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

    def _get_sg_entity_type(self, sg_data):
        """
        Return the SG entity type and fields associated with the given data, if the data represents
        SG data.

        :param sg_data: The dat to get the entity type from.
        :type sg_data: dict
        :return: The SG entity type, or None if the data is not valid SG data.
        :rtype: str
        """

        if not isinstance(sg_data, dict):
            return None

        entity_type = sg_data.get("type")

        # Sanity check that this is valid SG entity
        if shotgun_globals.is_valid_entity_type(entity_type, self.project_id):
            return entity_type

        # Last attempt to extract an entity type for the data - our source model may be a SG model which has an
        # instance method to get the entity type for the model data.
        try:
            source_model = self.get_source_model()
            return source_model.get_entity_type()
        except AttributeError:
            return None


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

        This acceptance defers from the `_proxy_filter_accepts_row` by only check the index
        acceptance based on a list of FilterItem objects, whereas the `_proxy_filter_accepts_row`
        uses the proxy model directly to check filter acceptance.

        This acceptance check omits any filters from the given field. This is to allow the
        FilterMenu to show filter groups where values from the filter group are OR'd together.

        :param index: The model index to check acceptance on.
        :type index: :class:`sgkt.platform.qt.QtCore.QModelIndex`
        :param field_id: Filters that belong to the field_id group are ignored when checking
                         acceptance.
        :type field_id: str
        :return: True if the index is accepted, else False
        :rtype: bool
        """

        filters = self._filter_menu.get_current_filters(exclude_fields=[field_id])

        if filters:
            if not FilterItem.do_filter(index, filters):
                return False

        return True
