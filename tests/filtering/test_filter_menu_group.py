# Copyright (c) 2021 Autoiesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import os
import sys

import pytest

import sgtk

try:
    from sgtk.platform.qt import QtCore, QtGui
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
from filter_menu_group import FilterMenuGroup


if os.environ.get("DEBUG_TESTS") == "1":
    sys.path.append("/Users/oues/python_libs")
    import ptvsd

    ptvsd.enable_attach()
    ptvsd.wait_for_attach()


####################################################################################################
# Fixtures
####################################################################################################


# @pytest.fixture()
# def filter_item(request):
#     """
#     Fixture to help generate a FilterItem object.
#     """

#     return FilterItem.create(
#         "filter.item.id",
#         {
#             "filter_type": request.param[0],
#             "filter_op": request.param[1],
#             "filter_role": 0,  # Dummy value required to create the FileItem
#         },
#     )


####################################################################################################
# FilterMenuGroup class Test cases
####################################################################################################


# @pytest.mark.parametrize(
#     "args,kwargs",
#     [
#         ((None, FilterItem.FilterType.GROUP, FilterItem.FilterOp.AND), {}),
#         (("test.filter.id", FilterItem.FilterType.GROUP, FilterItem.FilterOp.OR), {}),
#         (
#             ("test.filter.id", FilterItem.FilterType.BOOL, FilterItem.FilterOp.IS_TRUE),
#             {"filter_role": 0},
#         ),
#         (
#             (
#                 "test.filter.id",
#                 FilterItem.FilterType.STR,
#                 FilterItem.FilterOp.NOT_EQUAL,
#             ),
#             {"filter_role": 0},
#         ),
#         (
#             ("test.filter.id", FilterItem.FilterType.NUMBER, FilterItem.FilterOp.EQUAL),
#             {"filter_role": 0},
#         ),
#         (
#             ("test.filter.id", FilterItem.FilterType.LIST, FilterItem.FilterOp.EQUAL),
#             {"filter_role": 0},
#         ),
#         (
#             (
#                 "test.filter.id",
#                 FilterItem.FilterType.DATETIME,
#                 FilterItem.FilterOp.EQUAL,
#             ),
#             {"filter_role": 0},
#         ),
#         (
#             ("test.filter.id", FilterItem.FilterType.STR, FilterItem.FilterOp.IN),
#             {
#                 "filter_value": "some value",
#                 "filters": [
#                     FilterItem(
#                         "nested.filter.id",
#                         FilterItem.FilterType.GROUP,
#                         FilterItem.FilterOp.AND,
#                     )
#                 ],
#                 "filter_role": "some role",
#                 "data_func": lambda: True,
#             },
#         ),
#     ],
# )
# def test_filter_item_constructor(args, kwargs):
#     """
#     Test the FilterItem constructor.
#     """

#     result = FilterItem(*args, **kwargs)

#     assert result.id == args[0]
#     assert result.filter_type == args[1]
#     assert result.filter_op == args[2]
#     # TODO separate test methods to setting hte filter_value
#     # assert result.filter_value == kwargs.get("filter_value")
#     assert result.filters == (kwargs.get("filters") or [])
#     assert result.filter_role == kwargs.get("filter_role")
#     assert result.data_func == kwargs.get("data_func")

# def test_filter_menu_group_constructor():
#     pass

# def test_staticmethod_set_action_visible(action, visible):
#     pass

# def test_add_item(filter_item, filter_action):
#     pass
