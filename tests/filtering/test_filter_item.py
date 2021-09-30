# Copyright (c) 2021 Autoiesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

from datetime import datetime
import os
import sys

import pytest

import sgtk

try:
    from sgtk.platform.qt import QtCore
except:
    # components also use PySide, so make sure  we have this loaded up correctly
    # before starting auto-doc.
    from tank.util.qt_importer import QtImporter

    importer = QtImporter()
    sgtk.platform.qt.QtCore = importer.QtCore
    sgtk.platform.qt.QtGui = importer.QtGui

# Manually add the app modules to the path in order to import them here.
base_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "python")
)
filtering_dir = os.path.abspath(os.path.join(base_dir, "filtering"))
sys.path.extend([base_dir, filtering_dir])
from filter_item import FilterItem


####################################################################################################
# FilterITem Fixtures
####################################################################################################


@pytest.fixture()
def filter_item(request):
    """
    Fixture to help generate a FilterItem object.
    """

    return FilterItem.create(
        "filter.item.id",
        {
            "filter_type": request.param[0],
            "filter_op": request.param[1],
            "filter_role": 0,  # Dummy value required to create the FileItem
        },
    )


####################################################################################################
# FilterItem Test Cases
####################################################################################################


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ((None, FilterItem.FilterType.GROUP, FilterItem.FilterOp.AND), {}),
        (("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.OR), {}),
        (
            ("test.filter.id", FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_TRUE),
            {"filter_role": 0},
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.STR,
                FilterItem.FilterOp.NOT_EQUAL,
            ),
            {"filter_role": 0},
        ),
        (
            ("test.filter.id", FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL),
            {"filter_role": 0},
        ),
        (
            ("test.filter.id", FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL),
            {"filter_role": 0},
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.DATETIME,
                FilterItem.FilterOp.EQUAL,
            ),
            {"filter_role": 0},
        ),
        (
            ("test.filter.id", FilterItem.FilterType.STR, FilterItem.FilterOp.IN),
            {
                "filter_value": "some value",
                "filter_role": "some role",
                "data_func": lambda: True,
            },
        ),
    ],
)
def test_filter_item_constructor(args, kwargs):
    """
    Test the FilterItem constructor.
    """

    result = FilterItem(*args, **kwargs)

    assert result.id == args[0]
    assert result.filter_type == args[1]
    assert result.filter_op == args[2]
    assert result.filter_role == kwargs.get("filter_role")
    assert result.data_func == kwargs.get("data_func")


@pytest.mark.parametrize(
    "args,kwargs,expected_exception",
    [
        ((), {}, TypeError),
        (("test.filter.id"), {}, TypeError),
        (("test.filter.id", FilterItem.FilterType.GROUP), {}, TypeError),
        (
            ("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.AND),
            {"bad_kwarg": True},
            TypeError,
        ),
        (("test.filter.id", None, FilterItem.FilterOp.AND), {}, TypeError),
        (("test.filter.id", FilterItem.FilterType.GROUP, None), {}, TypeError),
        (
            ("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.EQUAL),
            {},
            TypeError,
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.GROUP,
                FilterItem.FilterOp.NOT_EQUAL,
            ),
            {},
            TypeError,
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.GROUP,
                FilterItem.FilterOp.IS_TRUE,
            ),
            {},
            TypeError,
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.GROUP,
                FilterItem.FilterOp.IS_FALSE,
            ),
            {},
            TypeError,
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.GROUP,
                FilterItem.FilterOp.GREATER_THAN,
            ),
            {},
            TypeError,
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.GROUP,
                FilterItem.FilterOp.GREATER_THAN_OR_EQUAL,
            ),
            {},
            TypeError,
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.GROUP,
                FilterItem.FilterOp.LESS_THAN,
            ),
            {},
            TypeError,
        ),
        (
            (
                "test.filter.id",
                FilterItem.FilterType.GROUP,
                FilterItem.FilterOp.LESS_THAN_OR_EQUAL,
            ),
            {},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.IN),
            {},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.NOT_IN),
            {},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.BOOL, FilterItem.FilterOp.AND),
            {},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.STR, FilterItem.FilterOp.OR),
            {},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.NUMBER, FilterItem.FilterOp.OR),
            {},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.LIST, FilterItem.FilterOp.OR),
            {},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.OR),
            {"filters": "bad value type"},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.OR),
            {"filters": 1},
            TypeError,
        ),
        (
            ("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.OR),
            {"filters": [1, "two", {}]},
            TypeError,
        ),
    ],
)
def test_filter_item_constructor_bad_args(args, kwargs, expected_exception):
    """
    Test the FilterItem constructor when passed incorrect arguments.
    """

    with pytest.raises(expected_exception):
        FilterItem(*args, **kwargs)


@pytest.mark.parametrize(
    "filter_id,data",
    [
        (
            "test.filter.id",
            {
                "filter_type": FilterItem.FilterType.STR,
                "filter_op": FilterItem.FilterOp.IN,
                "filter_role": 0,
            },
        ),
        (
            "test.filter.id",
            {
                "filter_type": FilterItem.FilterType.BOOL,
                "filter_op": FilterItem.FilterOp.IS_FALSE,
                "data_func": lambda: True,
            },
        ),
        (
            "test.filter.id",
            {
                "filter_type": FilterItem.FilterType.BOOL,
                "filter_op": FilterItem.FilterOp.IS_FALSE,
                "data_func": lambda: True,
                "filter_value": False,
            },
        ),
        (
            "test.filter.id",
            {
                "filter_type": FilterItem.FilterType.LIST,
                "filter_op": FilterItem.FilterOp.NOT_IN,
                "data_func": lambda: True,
                "filter_value": [
                    FilterItem(
                        "id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.OR
                    )
                ],
            },
        ),
    ],
)
def test_filter_item_class_method_create(filter_id, data):
    """
    Test the FilterItem factory classmethod "create".
    """

    result = FilterItem.create(filter_id, data)

    assert result.id == filter_id
    assert result.filter_type == data.get("filter_type")
    assert result.filter_op == data.get("filter_op")
    assert result.filter_role == data.get("filter_role")
    assert result.data_func == data.get("data_func")
    assert result.filters is None


@pytest.mark.parametrize(
    "op,group_filters,group_id",
    [
        (FilterItem.FilterOp.AND, None, None),
        (FilterItem.FilterOp.AND, [], None),
        (FilterItem.FilterOp.AND, [], "group.id"),
        (FilterItem.FilterOp.OR, None, None),
        (FilterItem.FilterOp.OR, [], None),
        (FilterItem.FilterOp.OR, [], "group.id"),
    ],
)
def test_filter_item_class_method_create_group(op, group_filters, group_id):
    """
    Test the FilterItem factory classmethod "create".
    """

    if group_filters is not None and group_id is not None:
        result = FilterItem.create_group(op, group_filters, group_id)
    elif group_filters is None:
        result = FilterItem.create_group(op, group_id=group_id)
    elif group_filters is None:
        result = FilterItem.create_group(op, group_filters=group_filters)
    else:
        result = FilterItem.create_group(op)

    assert result.id == (group_id or "{}.{}".format(FilterItem.FilterType.GROUP, op))
    assert result.filter_type == FilterItem.FilterType.GROUP
    assert result.filter_op == op
    assert result.filter_value == (group_filters or [])
    assert result.filters == result.filter_value
    assert result.filter_role is None
    assert result.data_func is None


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (None, None),
        (True, FilterItem.FilterType.BOOL),
        (False, FilterItem.FilterType.BOOL),
        ("", FilterItem.FilterType.STR),
        ("string", FilterItem.FilterType.STR),
        (1, FilterItem.FilterType.NUMBER),
        (int(1), FilterItem.FilterType.NUMBER),
        (1.0, FilterItem.FilterType.NUMBER),
        (float(1), FilterItem.FilterType.NUMBER),
        (complex(1), FilterItem.FilterType.NUMBER),
        ([], FilterItem.FilterType.LIST),
        ([1, 2, 3], FilterItem.FilterType.LIST),
        (["1", "2", "3"], FilterItem.FilterType.LIST),
        (datetime.now(), FilterItem.FilterType.DATETIME),
        (datetime.today(), FilterItem.FilterType.DATETIME),
        ({}, FilterItem.FilterType.DICT),
        ({"id": 0}, FilterItem.FilterType.DICT),
        ({"type": "any type"}, FilterItem.FilterType.DICT),
        ({"non-entity-key": "non-entity-value"}, FilterItem.FilterType.DICT),
        ({"value": None}, FilterItem.FilterType.DICT),
        ({"value": True}, FilterItem.FilterType.DICT),
        ({"value": False}, FilterItem.FilterType.DICT),
        ({"value": ""}, FilterItem.FilterType.DICT),
        ({"value": "string"}, FilterItem.FilterType.DICT),
        ({"value": 1}, FilterItem.FilterType.DICT),
        ({"value": int(1)}, FilterItem.FilterType.DICT),
        ({"value": 1.0}, FilterItem.FilterType.DICT),
        ({"value": float(1)}, FilterItem.FilterType.DICT),
        ({"value": complex(1)}, FilterItem.FilterType.DICT),
        ({"value": []}, FilterItem.FilterType.DICT),
        ({"value": [1, 2, 3]}, FilterItem.FilterType.DICT),
        ({"value": ["1", "2", "3"]}, FilterItem.FilterType.DICT),
        ({"value": datetime.now()}, FilterItem.FilterType.DICT),
        ({"value": datetime.today()}, FilterItem.FilterType.DICT),
    ],
)
def test_filter_item_classmethod_get_data_type(input_data, expected):
    """
    Test the classmethod 'get_data_type'.
    """

    # TODO unicode

    result = FilterItem.get_data_type(input_data)
    assert result == expected


@pytest.mark.parametrize(
    "input_type,expected",
    [
        (None, FilterItem.FilterOp.EQUAL),
        (FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL),
        (FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL),
        (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL),
        (FilterItem.FilterType.LIST, FilterItem.FilterOp.IN),
        (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
    ],
)
def test_filter_item_classmethod_default_op_for_type(input_type, expected):
    """
    Test the classmethod 'default_op_for_type'.

    This validates that the default operations for a given data type are as expected.
    If the default operations are updated, this test method will also need to be updated.
    """

    result = FilterItem.default_op_for_type(input_type)
    assert result == expected


@pytest.mark.parametrize(
    "input_op,expected",
    [
        (None, False),
        (FilterItem.FilterOp.EQUAL, False),
        (FilterItem.FilterOp.NOT_EQUAL, False),
        (FilterItem.FilterOp.IN, False),
        (FilterItem.FilterOp.NOT_IN, False),
        (FilterItem.FilterOp.IS_TRUE, False),
        (FilterItem.FilterOp.IS_FALSE, False),
        (FilterItem.FilterOp.GREATER_THAN, False),
        (FilterItem.FilterOp.GREATER_THAN_OR_EQUAL, False),
        (FilterItem.FilterOp.LESS_THAN, False),
        (FilterItem.FilterOp.LESS_THAN_OR_EQUAL, False),
        (FilterItem.FilterOp.OR, True),
        (FilterItem.FilterOp.AND, True),
    ],
)
def test_filter_item_classmethod_is_group_op(input_op, expected):
    """
    Test the classmethod 'is_group_op'.
    """

    result = FilterItem.is_group_op(input_op)
    assert result == expected


# TODO
# def test_filter_item_classmethod_do_filter(self):
#     """
#     """

#     assert False

# TODO
# def test_filter_item_classmethod_get_datetime_bucket(self):
#     """
#     """

#     assert False


@pytest.mark.parametrize(
    "filter_item,expected",
    [
        (FilterItem.create_group(FilterItem.FilterOp.AND), True),
        (FilterItem.create_group(FilterItem.FilterOp.AND), True),
        (
            FilterItem.create(
                "id",
                {
                    "filter_type": FilterItem.FilterType.GROUP,
                    "filter_op": FilterItem.FilterOp.OR,
                },
            ),
            True,
        ),
        (
            FilterItem.create(
                "id",
                {
                    "filter_type": FilterItem.FilterType.LIST,
                    "filter_op": FilterItem.FilterOp.IN,
                    "filter_role": 0,
                },
            ),
            False,
        ),
    ],
)
def test_filter_item_method_is_group(filter_item, expected):
    """
    Test the instance method 'is_group'.
    """

    result = filter_item.is_group()
    assert result == expected


# TODO
# def test_filter_item_method_get_index_data(self):
#     """
#     """

#     assert False

# TODO
# def test_filter_item_method_accepts(self):
#     """
#     """

#     assert False


@pytest.mark.parametrize(
    "filter_item,filter_value,input_value,expected",
    [
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_TRUE), None, True, True),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_TRUE), None, False, False),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_TRUE),
            None,
            "invalid bool",
            False,
        ),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_TRUE), None, None, False),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_FALSE), None, True, False),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_FALSE), None, False, True),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_FALSE),
            None,
            "invalid bool",
            False,
        ),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_FALSE), None, None, False),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL), True, True, True),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL), False, True, False),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL), True, False, False),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL), False, False, True),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL),
            True,
            "invalid bool",
            False,
        ),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL), True, None, False),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL),
            False,
            "invalid bool",
            False,
        ),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.EQUAL), False, None, False),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL),
            True,
            True,
            False,
        ),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL),
            False,
            True,
            True,
        ),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL),
            True,
            False,
            True,
        ),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL),
            False,
            False,
            False,
        ),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL),
            False,
            "invalid",
            True,
        ),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL),
            False,
            None,
            True,
        ),
        (
            (FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL),
            True,
            "invalid",
            True,
        ),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_EQUAL), True, None, True),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_bool_valid(
    filter_item, filter_value, input_value, expected
):
    """
    Test the instance method 'is_bool_valid'.
    """

    filter_item.filter_value = filter_value
    result = filter_item.is_bool_valid(input_value)

    assert result == expected


@pytest.mark.parametrize(
    "filter_item",
    [
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.IN)),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.NOT_IN)),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.LESS_THAN)),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.LESS_THAN_OR_EQUAL)),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.GREATER_THAN)),
        ((FilterItem.FilterType.BOOL, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL)),
    ],
    # indirect=["filter_item"],
    indirect=True,
)
def test_filter_item_method_is_bool_valid_bad_op(filter_item):
    """
    Test the instance method 'is_bool_valid' when the FilterItem has an invalid operation.
    """

    with pytest.raises(AssertionError):
        # The input value does not matter, since it should fail before trying to validate it.
        dummy_value = None
        filter_item.is_bool_valid(dummy_value)


@pytest.mark.parametrize(
    "filter_item,filter_value,input_value,expected",
    [
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), None, None, True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "", "", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "a", "a", True),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL),
            "abcd efgh ijk",
            "abcd efgh ijk",
            True,
        ),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), None, "", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "", None, False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "", "abc", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "abc", "", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "abc", "abcd", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "abcd", "abc", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL), "a", "A", False),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.EQUAL),
            "abcde",
            "abcdE",
            False,
        ),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), None, None, False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), "", "", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), "a", "a", False),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL),
            "abcd efgh ijk",
            "abcd efgh ijk",
            False,
        ),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), None, "", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), "", None, True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), "", "abc", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), "abc", "", True),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL),
            "abc",
            "abcd",
            True,
        ),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL),
            "abcd",
            "abc",
            True,
        ),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL), "a", "A", True),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_EQUAL),
            "abcde",
            "abcdE",
            True,
        ),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.IN),
            "",
            "abcd",
            True,
        ),  # NOTE is this actually what we want?
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), " ", "abcd", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), " ", " abcd", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), " ", "abcd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), " ", "ab cd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "a", "ab cd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "A", "ab cd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "ab", "abcd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "bcd", "abcd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "bc", "abcd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "abcd", "abcd ", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "xyz", "abcd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "axbcd", "abcd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "xabcd", "abcd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "abcdx", "abcd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IN), "abcx", "abcd ", False),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN),
            "",
            "abcd",
            False,
        ),  # NOTE is this actually what we want?
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), " ", "abcd", True),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), " ", " abcd", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), " ", "abcd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), " ", "ab cd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), "a", "ab cd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), "A", "ab cd ", False),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), "ab", "abcd ", False),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN),
            "bcd",
            "abcd ",
            False,
        ),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), "bc", "abcd ", False),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN),
            "abcd",
            "abcd ",
            False,
        ),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN), "xyz", "abcd ", True),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN),
            "axbcd",
            "abcd ",
            True,
        ),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN),
            "xabcd",
            "abcd ",
            True,
        ),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN),
            "abcdx",
            "abcd ",
            True,
        ),
        (
            (FilterItem.FilterType.STR, FilterItem.FilterOp.NOT_IN),
            "abcx",
            "abcd ",
            True,
        ),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_str_valid(
    filter_item, filter_value, input_value, expected
):
    """
    Test the instance method 'is_str_valid'.
    """

    filter_item.filter_value = filter_value
    result = filter_item.is_str_valid(input_value)

    assert result == expected


@pytest.mark.parametrize(
    "filter_item",
    [
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IS_TRUE)),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.IS_FALSE)),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.LESS_THAN)),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.LESS_THAN_OR_EQUAL)),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.GREATER_THAN)),
        ((FilterItem.FilterType.STR, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL)),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_str_valid_bad_op(filter_item):
    """
    Test the instance method 'is_str_valid' when the FilterItem has an invalid operation.
    """

    with pytest.raises(AssertionError):
        # The input value does not matter, since it should fail before trying to validate it.
        dummy_value = None
        filter_item.is_str_valid(dummy_value)


@pytest.mark.parametrize(
    "filter_item,filter_value,input_value,expected",
    [
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), None, None, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 0, None, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), None, 0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 0, 0, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 0, 0.0, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 1.234, 1.234, True),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL),
            1.234,
            1.2345,
            False,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 0, 1, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 0, 1.0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 1, 0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 1, 1.1, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL), 100, 100, True),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL),
            None,
            None,
            False,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), 0, None, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), None, 0, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), 0, 0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), 0, 0.0, False),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL),
            1.234,
            1.234,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL),
            1.234,
            1.2345,
            True,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), 0, 1, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), 1, 0, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), 0, 1.0, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL), 1, 1.1, True),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_EQUAL),
            100,
            100,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            None,
            None,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            0,
            None,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            None,
            0,
            False,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN), 0, 0, False),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            0,
            0.0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            0.0,
            0.0,
            False,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN), 0, 1, True),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            0,
            1.0,
            True,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN), 1, 0, False),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            1.0,
            0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            100,
            100,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            101,
            100,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            10,
            1001,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN),
            10.01,
            1001.0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            None,
            None,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            0,
            None,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            None,
            0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            0,
            0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            0,
            0.0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            0.0,
            0.0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            0,
            1,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            0,
            1.0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            1,
            0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            1.0,
            0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            100,
            100,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            101,
            100,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            10,
            1001,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL),
            10.01,
            1001,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN),
            None,
            None,
            False,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 0, None, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), None, 0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 0, 0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 0, 0.0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 0.0, 0, False),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN),
            0.0,
            0.0,
            False,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 0, 1, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 0, 1.0, False),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 1, 0, True),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 1.0, 0, True),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN),
            100,
            100,
            False,
        ),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN), 101, 100, True),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN),
            10,
            1001,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN),
            10.01,
            1001.0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            None,
            None,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            0,
            None,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            None,
            0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            0,
            0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            0,
            0.0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            0.0,
            0.0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            0,
            1,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            0,
            1.0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            1,
            0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            1.0,
            0,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            100,
            100,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            101,
            100,
            True,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            10,
            1001,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            10.01,
            1001.0,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            10.01,
            10.10,
            False,
        ),
        (
            (FilterItem.FilterType.NUMBER, FilterItem.FilterOp.LESS_THAN_OR_EQUAL),
            10.01,
            10.00,
            True,
        ),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_number_valid(
    filter_item, filter_value, input_value, expected
):
    """
    Test the instance method 'is_number_valid'.
    """

    filter_item.filter_value = filter_value
    result = filter_item.is_number_valid(input_value)

    assert result == expected


@pytest.mark.parametrize(
    "filter_item",
    [
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.IN)),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.NOT_IN)),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.IS_FALSE)),
        ((FilterItem.FilterType.NUMBER, FilterItem.FilterOp.IS_TRUE)),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_number_valid_bad_op(filter_item):
    """
    Test the instance method 'is_number_valid' when the FilterItem has an invalid operation.
    """

    with pytest.raises(AssertionError):
        # The input value does not matter, since it should fail before trying to validate it.
        dummy_value = 0
        filter_item.filter_value = 0
        filter_item.is_number_valid(dummy_value)


@pytest.mark.parametrize(
    "filter_item,filter_value,input_value,expected",
    [
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL), None, None, True),
        (
            (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
            None,
            datetime.today(),
            False,
        ),
        (
            (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
            datetime.today(),
            None,
            False,
        ),
        (
            (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
            None,
            datetime.now(),
            False,
        ),
        (
            (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
            datetime.now(),
            None,
            False,
        ),
        (
            (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
            "Today",
            "Today",
            True,
        ),
        (
            (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
            "Today",
            "Yesterday",
            False,
        ),
        (
            (FilterItem.FilterType.DATETIME, FilterItem.FilterOp.EQUAL),
            "Tomorrow",
            "Yesterday",
            False,
        ),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_datetime_valid(
    filter_item, filter_value, input_value, expected
):
    """
    Test the instance method 'is_datetime_valid'.
    """

    filter_item.filter_value = filter_value
    result = filter_item.is_datetime_valid(input_value)

    assert result == expected


@pytest.mark.parametrize(
    "filter_item",
    [
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.IN)),
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.NOT_IN)),
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.IS_FALSE)),
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.IS_TRUE)),
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.GREATER_THAN)),
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL)),
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.LESS_THAN)),
        ((FilterItem.FilterType.DATETIME, FilterItem.FilterOp.LESS_THAN_OR_EQUAL)),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_datetime_valid_bad_op(filter_item):
    """
    Test the instance method 'is_str_valid' when the FilterItem has an invalid operation.
    """

    with pytest.raises(AssertionError):
        # The input value does not matter, since it should fail before trying to validate it.
        dummy_value = None
        filter_item.is_datetime_valid(dummy_value)


@pytest.mark.parametrize(
    "filter_item,filter_value,input_value,expected",
    [
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), None, None, True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), [], None, False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), None, [], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), None, [None], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), [], [], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), [], [1], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), [1], [], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), [1], [1], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), ["1"], [1], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL), ["1"], ["1"], True),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL),
            [1, 2, 3],
            [1, 2, 3],
            True,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL),
            [1, 2, 3],
            [1, 2, 3, 4],
            False,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL),
            None,
            None,
            False,
        ),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL), [], None, True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL), None, [], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL), [], [], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL), [], [1], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL), [1], [], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL), [1], [1], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL), ["1"], [1], True),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL),
            ["1"],
            ["1"],
            False,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL),
            [1, 2, 3],
            [1, 2, 3],
            False,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_EQUAL),
            [1, 2, 3],
            [1, 2, 3, 4],
            True,
        ),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), None, None, True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), [], None, True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), None, [], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), None, [None], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), [], [], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), [], [1], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), [1], [], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), [1], [1], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), ["1"], [1], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), ["1"], ["1"], True),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.IN),
            [1, 2, 3],
            [1, 2, 3],
            True,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.IN),
            [1, 2, 3],
            [1, 2, 3, 4],
            True,
        ),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), [1, 2, 3], [2, 4], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IN), [1, 2, 3], [4], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), None, None, False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), [], None, False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), None, [], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), None, [None], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), [], [], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), [], [1], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), [1], [], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), [1], [1], False),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), ["1"], [1], True),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN), ["1"], ["1"], False),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN),
            [1, 2, 3],
            [1, 2, 3],
            False,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN),
            [1, 2, 3],
            [1, 2, 3, 4],
            False,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN),
            [1, 2, 3],
            [2, 4],
            False,
        ),
        (
            (FilterItem.FilterType.LIST, FilterItem.FilterOp.NOT_IN),
            [1, 2, 3],
            [4],
            True,
        ),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_list_valid(
    filter_item, filter_value, input_value, expected
):
    """
    Test the instance method 'is_list_valid'.
    """

    filter_item.filter_value = filter_value
    result = filter_item.is_list_valid(input_value)

    assert result == expected


@pytest.mark.parametrize(
    "filter_item",
    [
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IS_FALSE)),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.IS_TRUE)),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.GREATER_THAN)),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL)),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.LESS_THAN)),
        ((FilterItem.FilterType.LIST, FilterItem.FilterOp.LESS_THAN_OR_EQUAL)),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_list_valid_bad_op(filter_item):
    """
    Test the instance method 'is_list_valid' when the FilterItem has an invalid operation.
    """

    with pytest.raises(AssertionError):
        # The input value does not matter, since it should fail before trying to validate it.
        dummy_value = [1]
        filter_item.filter_value = [1]
        filter_item.is_list_valid(dummy_value)


@pytest.mark.parametrize(
    "filter_item,filter_value,input_value,expected",
    [
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL), None, None, True),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL), {}, None, False),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL), None, {}, False),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL), {}, {}, True),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL), {"id": 1}, {}, False),
        (
            (FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL),
            {"id": 1},
            {"id": 0},
            False,
        ),
        (
            (FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL),
            {"id": 1},
            {"not-id": 1},
            False,
        ),
        (
            (FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL),
            {"id": 1},
            {"id": 1},
            True,
        ),
        (
            (FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL),
            {"id": 1, "type": "a"},
            {"id": 1, "type": "b"},
            False,
        ),
        (
            (FilterItem.FilterType.DICT, FilterItem.FilterOp.EQUAL),
            {"id": 1, "type": "a"},
            {"id": 1, "type": "a"},
            True,
        ),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_dict_valid(
    filter_item, filter_value, input_value, expected
):
    """
    Test the instance method 'is_dict_valid'.
    """

    filter_item.filter_value = filter_value
    result = filter_item.is_dict_valid(input_value)

    assert result == expected


@pytest.mark.parametrize(
    "filter_item",
    [
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.IN)),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.NOT_IN)),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.IS_FALSE)),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.IS_TRUE)),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.GREATER_THAN)),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.GREATER_THAN_OR_EQUAL)),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.LESS_THAN)),
        ((FilterItem.FilterType.DICT, FilterItem.FilterOp.LESS_THAN_OR_EQUAL)),
    ],
    indirect=["filter_item"],
)
def test_filter_item_method_is_dict_valid_bad_op(filter_item):
    """
    Test the instance method 'is_list_valid' when the FilterItem has an invalid operation.
    """

    with pytest.raises(AssertionError):
        # The input value does not matter, since it should fail before trying to validate it.
        dummy_value = None
        filter_item.is_dict_valid(dummy_value)
