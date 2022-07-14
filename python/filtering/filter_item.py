# Copyright (c) 2021 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.
from datetime import datetime, timedelta
import numbers

import sgtk
from sgtk.platform.qt import QtCore
from tank_vendor import six
from tank_vendor.shotgun_api3 import sg_timezone


class FilterItem(object):
    """
    Class object to encapsulate all the necessary data to filter model index data.

    A FilterItem properties:

        filter type:
            This determines how the incoming data is processed and filtered, and is most
            likely determined based on the filter value data type. See supported filter types
            in FilterType enum class.
        filter_op:
            This determines the operation that is applied on filtering the data. See supported
            filter operations in FilterOp enum class.
        filter_value:
            This is the value that incoming data is compared against, when filtering. For group
            filter items, this will be the list of filter items the group uses for filtering.
        filters:
            This is a convenience property to access the filter items for a group filter.
        filter_role:
            The model item data role that will be used to extract the data from incoming indexes
            to be filtered. This is optional, but if not defined, then a `data_func` must be
            defined.
        data_func:
            This is a function that is used to extract the data from incoming indexes to be
            filterd. This is option, but if not defined, then a `filter_role` must be defined.

    To filter an index by a FilterItem, call the `accepts` method, e.g.:
        filter_item.accepts(index)

    To filter an index by a group of FilterItems, the `accept` method can be used the same as non-group
    filters, or the classmethod FilterItem.do_filter(index, filters, filter_op) may be used. When filtering
    using groups of FilterItems, the individual results of the FilterItem accept tests are AND'ed or OR'ed
    together based on the group. The filter groups can be nested by including a group filter in the group
    filters list.
    """

    class FilterOp(object):
        """
        Enum class for filter operations.
        """

        AND = "and"
        OR = "or"
        IS_TRUE = "true"
        IS_FALSE = "false"
        IN = "in"
        NOT_IN = "!in"
        EQUAL = "="
        NOT_EQUAL = "!="
        LESS_THAN = "<"
        LESS_THAN_OR_EQUAL = "<="
        GREATER_THAN = ">"
        GREATER_THAN_OR_EQUAL = ">="

        # The valid filter operations. Any type added above must be added to this tuple.
        VALID_OPS = (
            AND,
            OR,
            IS_TRUE,
            IS_FALSE,
            IN,
            NOT_IN,
            EQUAL,
            NOT_EQUAL,
            LESS_THAN,
            LESS_THAN_OR_EQUAL,
            GREATER_THAN,
            GREATER_THAN_OR_EQUAL,
        )

    class FilterType(object):
        """
        Enum class for filter types.
        """

        BOOL = "bool"
        STR = "str"
        NUMBER = "number"
        LIST = "list"
        DICT = "dict"
        DATE = "date"
        DATETIME = "date_time"
        # Special type used for grouping filter items
        GROUP = "group"

        # The valid filter types. Any type added above must be added to this tuple.
        VALID_TYPES = (
            BOOL,
            STR,
            NUMBER,
            LIST,
            DATETIME,
            DICT,
            GROUP,
        )

        # A mapping of data types to the basic set of filter types defined here, to keep a small
        # consistent set of types. This is mostly for mapping SG data types.
        MAP_TYPES = {
            "text": STR,
            "status_list": STR,
            "date": DATETIME,
            "url": DICT,
            "entity": DICT,
            "multi_entity": LIST,
        }

    # The default operation for a given filter type.
    DEFAULT_OPS = {
        FilterType.LIST: FilterOp.IN,
        FilterType.STR: FilterOp.EQUAL,
        FilterType.NUMBER: FilterOp.EQUAL,
        FilterType.BOOL: FilterOp.EQUAL,
        FilterType.DICT: FilterOp.EQUAL,
        FilterType.DATETIME: FilterOp.EQUAL,
        FilterType.GROUP: FilterOp.AND,
    }

    # Datetime objects may be processed into a 'bucket' for filtering.
    DATETIME_BUCKETS = (
        "Today",
        "Yesterday",
        "Tomorrow",
        "Far Future",
        "Long Ago",
        "Last Few Months",
        "Next Few Months",
        "Last Few Weeks",
        "Last Week",
        "This Week",
        "Next Week",
        "Next Few Weeks",
        "No Date",
    )

    def __init__(
        self,
        filter_id,
        filter_type,
        filter_op,
        filter_value=None,
        filter_role=None,
        data_func=None,
    ):
        """
        Constructor.

        Validate the data on creating the object.

        :param filter_type: The data type for the filter
        :type filter_type: FilterType
        :param filter_op: The operation the filter will apply.
        :type filter_op: FilterOp
        :param filter_role: An item data role to extract the index data to filter based on (optional).
        :type filter_role: :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`
        :param data_func: A function that can be called to extract the index data to filter based on (optional).
                          NOTE: if a filter_role is defined, this will have no effect.
        :param filter_value: The value the item's data will be filtered by (optional). This value may be set
                             later (dynamically), if not known at time of init.
        :type filter_value: The data type for this filter
        :param filters: A list of FilterItem objects (optional). This is used for group filters; this list of
                        filter items are the group of filters to apply to the data.
        :type filters: list<FilterItem>
        """

        is_group_filter = filter_type is self.FilterType.GROUP
        has_group_op = self.is_group_op(filter_op)
        if is_group_filter != has_group_op:
            raise TypeError(
                ("Group filter types can only be used with group filter operations"),
                ("and non-group filters types can not use group filter operations"),
            )

        # For non group filter items, there must be a filter role or data function passed so that index data
        # can be retrieved on checking if an index is accepted by the filter item.
        if not is_group_filter and filter_role is None and data_func is None:
            raise ValueError(
                "Missing required 'filter_role' or 'data_func' to create FilterItem object"
            )

        self._id = filter_id
        self.filter_type = filter_type
        self.filter_op = filter_op
        self.filter_value = filter_value
        self.filter_role = filter_role
        self.data_func = data_func

        # Define a look up for filter function based on the filter type.
        self._filter_funcs_by_type = {
            self.FilterType.BOOL: self.is_bool_valid,
            self.FilterType.STR: self.is_str_valid,
            self.FilterType.DATETIME: self.is_datetime_valid,
            self.FilterType.NUMBER: self.is_number_valid,
            self.FilterType.LIST: self.is_list_valid,
            self.FilterType.DICT: self.is_dict_valid,
        }

    def __repr__(self):
        """
        Return a string representation for the FilterItem.
        """

        params = {
            "id": self._id,
            "value": self.filter_value,
        }
        params_str = ", ".join(
            ["{}={}".format(key, value) for key, value in params.items()]
        )

        return "<{class_name} {params}>".format(
            class_name=self.__class__.__name__, params=params_str
        )

    @property
    def id(self):
        """
        Get the id for this FilterItem.
        """

        return self._id

    @property
    def filter_type(self):
        """
        Get or set the filter type.
        """

        return self._filter_type

    @filter_type.setter
    def filter_type(self, value):
        """
        Process the value to be set as the filter's type. This is to ensure the simplist set of
        filter types; for example, SG has its own set of "types" for SG data, this method will
        ensure the SG data type is mapped to the appropriate filter type.
        """

        if value not in (self.FilterType.VALID_TYPES):
            value = self.FilterType.MAP_TYPES.get(value)

        if not value:
            raise TypeError("Invalid filter type '{}'".format(value))

        self._filter_type = value

    @property
    def filter_op(self):
        """
        Get or set the filter operation.
        """

        return self._filter_op

    @filter_op.setter
    def filter_op(self, value):

        if value not in self.FilterOp.VALID_OPS:
            raise TypeError("Invalid filter operation '{}'.".format(value))

        self._filter_op = value

    @property
    def filter_value(self):
        """
        Get or set the value for the filter that incoming data will be compared against to check
        acceptance.
        """

        return self._filter_value

    @filter_value.setter
    def filter_value(self, value):
        """
        Validate the data to be set as the filter's value.
        """

        if isinstance(value, dict) and self.filter_type not in (
            self.FilterType.DICT,
            self.FilterType.LIST,
        ):
            # Try to extract the value from the dictionary object, for filter types that
            # are not expected a dictionary value.
            value = value.get("value")

        if value is None:
            # Just leave it as is
            pass

        elif self.filter_type == self.FilterType.GROUP:
            if value is None:
                value = []

            if not isinstance(value, list):
                raise TypeError(
                    "Attempting to set invalid value '{value}' for '{type}' filter type".format(
                        value=value, type=self.filter_type
                    )
                )

            for filter_item in value:
                if not isinstance(filter_item, FilterItem):
                    raise TypeError(
                        "Attempting to set invalid value group filter '{item}'. Must be a FilterItem".format(
                            item=filter_item
                        )
                    )

        elif self.filter_type == self.FilterType.BOOL:
            # Allow 0 and 1 to be coerced to False and True. Do not allow any other non-bool data
            # types to go through, this could cause misleading filtering.
            if value == 0:
                value = False
            elif value == 1:
                value = True

            if not isinstance(value, bool):
                raise TypeError(
                    "Attempting to set invalid value '{value}' for '{type}' filter type".format(
                        value=value, type=self.filter_type
                    )
                )

        elif self.filter_type == self.FilterType.STR:
            if not isinstance(value, six.string_types):
                # Just coerce it to string type.
                value = str(value)

        elif self.filter_type == self.FilterType.NUMBER:
            if isinstance(value, six.string_types):
                # For string values, first try to coerce to an int.
                try:
                    value = int(value)
                except ValueError:
                    pass

            if isinstance(value, six.string_types):
                # Still a string value, next try to coerce to a float.
                try:
                    value = float(value)
                except ValueError:
                    pass

            if not isinstance(value, numbers.Number):
                raise TypeError(
                    "Attempting to set invalid value '{value}' for '{type}' filter type".format(
                        value=value, type=self.filter_type
                    )
                )

        elif self.filter_type == self.FilterType.DICT:
            if not isinstance(value, (dict, six.string_types)):
                raise TypeError(
                    "Attempting to set invalid value '{value}' for '{type}' filter type".format(
                        value=value, type=self.filter_type
                    )
                )

        elif self.filter_type == self.FilterType.DATETIME:
            # Allow string values that are a valid "datetime" bucket or datetime objects
            valid = False
            if isinstance(value, six.string_types):
                valid = value in self.DATETIME_BUCKETS

            if not valid:
                if isinstance(value, six.string_types):
                    value = datetime.strptime(value, "%Y-%m-%d")
                    value.replace(tzinfo=sg_timezone.LocalTimezone())

                if isinstance(value, float):
                    value = datetime.fromtimestamp(
                        value, tz=sg_timezone.LocalTimezone()
                    )

                if not isinstance(value, datetime):
                    raise TypeError(
                        "Attempting to set invalid value '{value}' for '{type}' filter type".format(
                            value=value, type=self.filter_type
                        )
                    )

        self._filter_value = value

    @property
    def filters(self):
        """
        Get or set the list of filter items for this group filter. This is a convenience property for
        group filter items, and hides the internal implementation details of storing the filters in
        the filter items `filter_value`.
        """

        if self.is_group():
            return self.filter_value

        # Non-group filter items do not have a list of filter items.
        return None

    @filters.setter
    def filters(self, value):
        if self.is_group():
            self.filter_value = value

    @property
    def filter_role(self):
        """
        Get or set the model item data role used to extract data from incoming indexes to be filtered.
        """

        return self._filter_role

    @filter_role.setter
    def filter_role(self, value):
        self._filter_role = value

    @property
    def data_func(self):
        """
        Get or set the function used to extract data from incoming indexes to be filtered.
        """

        return self._data_func

    @data_func.setter
    def data_func(self, value):
        if value and not callable(value):
            raise TypeError(
                "Invalid data function '{}'. Must be callable.".format(value)
            )

        self._data_func = value

    @classmethod
    def create(cls, filter_id, data):
        """
        Convenience factory classmethod to create a new FilterItem object from the provided data.

        :param data: The data to create the FilterItem object from.
        :type data: dict

        :return: The created FilterItem object
        :rtype: FilterItem
        """

        return cls(
            filter_id,
            data.get("filter_type"),
            data.get("filter_op"),
            filter_value=data.get("filter_value"),
            filter_role=data.get("filter_role"),
            data_func=data.get("data_func"),
        )

    @classmethod
    def create_group(cls, op, group_filters=None, group_id=None):
        """
        Convenience factory method to create a new FilterItem object that is a group.

        :param op: The group operation to set for this filter item.
        :type op: FilterOp
        :param group_filters: The list of FilterItems for this group filter (optional).
        :type group_filters: list<FilterItem>
        :param group_id: The identifier for the group (optional). If none given,
                         the filter item will have id "FilterType.FilterOp".
        :type group_id: str

        :return: The created FilterItem object whose type is FilterType.GROUP
        :rtype: FilterItem
        """

        filters = group_filters or []
        filter_id = group_id or "{type}.{op}".format(type=cls.FilterType.GROUP, op=op)

        return FilterItem(filter_id, cls.FilterType.GROUP, op, filter_value=filters)

    @classmethod
    def get_data_type(cls, data):
        """
        Return the FilterItem type for the given data.

        :param data: The data to get the type for.
        :type data: any

        :return: The FilterItem type of the data. None is returned for invalid data.
        :rtype: FilterType
        """

        if isinstance(data, bool):
            return cls.FilterType.BOOL

        if isinstance(data, six.string_types):
            return cls.FilterType.STR

        if isinstance(data, numbers.Number):
            return cls.FilterType.NUMBER

        if isinstance(data, list):
            return cls.FilterType.LIST

        if isinstance(data, datetime):
            return cls.FilterType.DATETIME

        if isinstance(data, dict):
            return cls.FilterType.DICT

        # Should we have an explicit type for None?
        return None

    @classmethod
    def default_op_for_type(cls, filter_type):
        """
        Return the default operation for the given filter data type.

        :param filter_type: One of the defined FilterItem types; e.g. FilterItem.FilterType.{name}.
        :type filter_type: str

        :return: The default operation to apply to the given filter type.
        :rtype: str, one of the FilterItem operations defined in the class; e.g. FilterItem.FilterOp.{name}.
        """

        return cls.DEFAULT_OPS.get(filter_type, cls.FilterOp.EQUAL)

    @classmethod
    def is_group_op(cls, op):
        """
        Return True if the filter item operation is valid.

        :param op: The operation to check.
        :type op: FilterOp

        :return: True if the op is a group operation, else False.
        :rtype: bool
        """

        return op in (cls.FilterOp.AND, cls.FilterOp.OR)

    @classmethod
    def do_filter(cls, index, filter_items, op=FilterOp.AND):
        """
        Return True if the index is accepted by the list of filter items.

        :param index: The index to check acceptance on.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
        :param filter_items: The list of filter items used to check acceptance.
        :type filter_items: list<FilterItem>
        :param op: The filter operation to apply with checking acceptance.
        :type op: FilterOp

        :return: True if accepted, else False.
        :rtype: bool
        """

        if not cls.is_group_op(op):
            raise ValueError("Invalid filter group operation {}".format(op))

        for filter_item in filter_items:
            if filter_item.is_group():
                if not filter_item.filters:
                    # Just accept empty groups
                    accepted = True
                else:
                    accepted = cls.do_filter(
                        index, filter_item.filters, filter_item.filter_op
                    )
            else:
                accepted = filter_item.accepts(index)

            if op == cls.FilterOp.AND and not accepted:
                return False

            if op == cls.FilterOp.OR and accepted:
                return True

        if op == cls.FilterOp.AND:
            # Accept if the operation is AND since it would have been rejected immediately if
            # any filter item did not accept it.
            return True

        # Do not accept if the operation is OR (or invalid) since the value would have
        # been accepted immediately if any filters accepted it.
        return False

    @staticmethod
    def get_datetime_bucket(dt):
        """
        This attempts to get the datetime bucket for the given datetime passed. Datetime buckets
        follow the same logic as the ShotGrid Web UI.

        NOTE should we move this to shotgun_globals.date_time module?

        :param dt: The datetime value to process
        :type dt: str | float | datetime.datetime

        :return: The datetime bucket that this datetime value falls into.
        :rtype: str
        """

        if dt is None:
            return "No Date"

        if isinstance(dt, six.string_types):
            if dt in FilterItem.DATETIME_BUCKETS:
                return dt

            dt = datetime.strptime(dt, "%Y-%m-%d")
            dt.replace(tzinfo=sg_timezone.LocalTimezone())

        if isinstance(dt, float):
            dt = datetime.fromtimestamp(dt, tz=sg_timezone.LocalTimezone())

        if not isinstance(dt, datetime):
            raise TypeError(
                "Cannot convert value type '{}' to datetime".format(type(dt))
            )

        # NOTE
        # Date comparisons - the ordering of the comparisons affect the result
        # The return value must be one of the values defined in DATETIME_BUCKETS
        #
        now = datetime.now(sg_timezone.LocalTimezone())
        today = now.date()
        date_value = dt.date()
        if date_value == today:
            return "Today"

        yesterday = now - timedelta(days=1)
        if date_value == yesterday.date():
            return "Yesterday"

        tomorrow = now + timedelta(days=1)
        if date_value == tomorrow.date():
            return "Tomorrow"

        # ShotGrid Web UI calculates Far Future as more than 120 days (30 days times 4, roughly 4 months)
        far_future = today + timedelta(days=30 * 4)
        if date_value > far_future:
            return "Far Future"

        # ShotGrid Web UI calculates Long Ago similarly to Far Future
        long_ago = today - timedelta(days=30 * 4)
        if date_value < long_ago:
            return "Long Ago"

        # ShotGrid Web UI calculates months ago as at least four weeks passed
        four_weeks_ago = today - timedelta(weeks=4)
        if date_value < four_weeks_ago:
            return "Last Few Months"
        # And similarly for next months ahead
        four_weeks_ahead = today + timedelta(weeks=4)
        if date_value > four_weeks_ahead:
            return "Next Few Months"

        # ShotGrid Web UI calculates week boundaries from Sunday; e.g. Last week will be any day from today
        # until (and including) last Sunday
        # Past weeks
        days_since_sunday = today.weekday() + 1
        last_last_sunday = today - timedelta(days=days_since_sunday, weeks=1)
        if date_value < last_last_sunday:
            return "Last Few Weeks"

        last_sunday = today - timedelta(days=days_since_sunday)
        if date_value < last_sunday:
            return "Last Week"

        next_sunday = today + timedelta(days=-days_since_sunday, weeks=1)
        if last_sunday <= date_value < next_sunday:
            return "This Week"

        next_next_sunday = today + timedelta(days=-days_since_sunday, weeks=2)
        if date_value < next_next_sunday:
            return "Next Week"

        if date_value <= four_weeks_ahead:
            return "Next Few Weeks"

        assert (
            False
        ), "Datetime value was not able to be converted to bucket, will default to plain datetime string"
        return dt.strftime("%x")

    def is_group(self):
        """
        :return: True if this filter item is a group, else False.
        :rtype: bool
        """

        return self.filter_type == self.FilterType.GROUP and self.is_group_op(
            self.filter_op
        )

    def get_index_data(self, index):
        """
        Return the index's data based on the filter item. The index data will be first
        attempted to be retrieved from the index's data method, using the filter role.
        If no role is defined, the data_func will be called to extract the data (if such
        a function is defined).

        A `filter_role` or `data_func` must be defined to reteieve the index data.

        :param index: The index to get the data from
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: The index data
        :rtype: any
        """

        if self.filter_role is not None:
            return index.data(self.filter_role)

        if self.data_func:
            return self.data_func(index)

        assert (
            False
        ), "FilterItem does not have a filter role or data function to retrieve index data to filter on"
        return None

    def accepts(self, index):
        """
        Return True if this filter item accepts the given index.

        :param index: The index that holds the data to filter on.
        :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

        :return: True if the filter accepts the index, else False.
        :rtype: bool
        """

        if self.is_group():
            # Filter by the group filters
            return self.do_filter(index, self.filters, self.filter_op)

        # Filter based on a single filter item
        data = self.get_index_data(index)
        filter_func = self._filter_funcs_by_type.get(self.filter_type, None)

        if filter_func is None:
            return False  # Invalid filter type

        return filter_func(data)

    def is_bool_valid(self, value):
        """
        Filter the incoming boolean value.

        :param value: The value to filter.
        :type value: bool

        :return: True if the filter accepts the value, else False.
        :rtype: bool
        """

        if self.filter_op == self.FilterOp.IS_TRUE:
            return value is True

        if self.filter_op == self.FilterOp.IS_FALSE:
            return value is False

        if self.filter_op == self.FilterOp.EQUAL:
            return value == self.filter_value

        if self.filter_op == self.FilterOp.NOT_EQUAL:
            return value != self.filter_value

        assert False, "Unsupported operation '{op}' for filter type '{type}'".format(
            op=self.filter_op, type=type(bool)
        )
        return False

    def is_str_valid(self, value):
        """
        Filter the incoming string value.

        :param value: The value to filter.
        :type value: str

        :return: True if the filter accepts the value, else False.
        :rtype: bool
        """

        if self.filter_op == self.FilterOp.EQUAL:
            return value == self.filter_value

        if self.filter_op == self.FilterOp.NOT_EQUAL:
            return value != self.filter_value

        if self.filter_op in (self.FilterOp.IN, self.FilterOp.NOT_IN):
            if self.filter_value is None:
                self.filter_value = ""
            if value is None:
                value = ""

            regex = QtCore.QRegExp(
                self.filter_value, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString
            )
            match = regex.indexIn(value)

            if self.filter_op == self.FilterOp.IN:
                return match >= 0

            if self.filter_op == self.FilterOp.NOT_IN:
                return match < 0

        assert False, "Unsupported operation for filter type 'str'"
        return False

    def is_number_valid(self, value):
        """
        Filter the incoming number value.

        :param value: The value to filter.
        :type value: int | float | ...

        :return: True if the filter accepts the value, else False.
        :rtype: bool
        """

        if isinstance(value, dict):
            value = value.get("value")

        if self.filter_op == self.FilterOp.EQUAL:
            return value == self.filter_value

        if self.filter_op == self.FilterOp.NOT_EQUAL:
            return value != self.filter_value

        if value is None or self.filter_value is None:
            # aAnnot apply greater/less than operations on None values
            return False

        if self.filter_op == self.FilterOp.GREATER_THAN:
            return value > self.filter_value

        if self.filter_op == self.FilterOp.GREATER_THAN_OR_EQUAL:
            return value >= self.filter_value

        if self.filter_op == self.FilterOp.LESS_THAN:
            return value < self.filter_value

        if self.filter_op == self.FilterOp.LESS_THAN_OR_EQUAL:
            return value <= self.filter_value

        assert False, "Unsupported operation for filter type 'number'"
        return False

    def is_datetime_valid(self, value):
        """
        Filter the incoming datetime value.

        TODO support operations like greater/less than and between.

        :param value: The value to filter.
        :type value: str | datetime.datetime

        :return: True if the filter accepts the value, else False.
        :rtype: bool
        """

        if isinstance(self.filter_value, six.string_types):
            value = self.get_datetime_bucket(value)

        if self.filter_op == self.FilterOp.EQUAL:
            return value == self.filter_value

        if self.filter_op == self.FilterOp.NOT_EQUAL:
            return value != self.filter_value

        assert False, "Unsupported operation for filter type 'datetime'"
        return False

    def is_list_valid(self, values_list):
        """
        Filter the incoming list value.

        :param value: The values list to filter by.
        :type value: list

        :return: True if the filter accepts the values list, else False.
        :rtype: bool
        """

        if self.filter_op == self.FilterOp.EQUAL:
            return values_list == self.filter_value

        if self.filter_op == self.FilterOp.NOT_EQUAL:
            return values_list != self.filter_value

        # IN/NOT_IN operations will check if there are any common elements within both value lists,
        # so convert incoming and filter value to a list.
        if not isinstance(values_list, list):
            values_list = [values_list]

        if not isinstance(self.filter_value, list):
            filter_values = [self.filter_value]
        else:
            filter_values = self.filter_value

        if self.filter_op == self.FilterOp.IN:
            # Handle None/empty lists - we consider it to be valid if either the incoming values
            # list or the filter value is an empty list, and the other contains the 'None' value.
            if not values_list:
                return None in filter_values

            if not filter_values:
                return None in values_list

            for value in values_list:
                for filter_value in filter_values:
                    if value == filter_value:
                        return True
            return False

        if self.filter_op == self.FilterOp.NOT_IN:
            # Handle None/empty lists - we consider it to be valid if either the incoming values
            # list or the filter value is an empty list, and the other does NOT contains the
            # 'None' value.
            if not values_list:
                return None not in filter_values

            if not filter_values:
                return None not in values_list

            for value in values_list:
                for filter_value in filter_values:
                    if value == filter_value:
                        return False
            return True

        assert False, "Unsupported operation for filter type 'list'"
        return False

    def is_dict_valid(self, value):
        """
        Filter the incoming dictionary value.

        :param value: The values list to filter by.
        :type value: list

        :return: True if the filter accepts the values list, else False.
        :rtype: bool
        """

        if self.filter_op == self.FilterOp.EQUAL:
            return value == self.filter_value

        if self.filter_op == self.FilterOp.NOT_EQUAL:
            return value != self.filter_value

        assert False, "Unsupported operation for filter type `{type}`".format(
            type=self.filter_type
        )
        return False
