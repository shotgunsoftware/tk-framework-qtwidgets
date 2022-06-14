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

import mock
from mock import Mock, patch
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
    from sgtk.platform.qt import QtCore


from tank_test.tank_test_base import TankTestBase
from tank_test.tank_test_base import setUpModule  # noqa

from list_model import _TestListModel
from data_object import _TestDataObject


class TestFiltersDefinition(TankTestBase):
    """
    Test the filtering FilterDefinition class.
    """

    def setUp(self):
        """
        Start the test engine, import the necessary frameworks for testing, and initialize some basic model data.
        """

        super(TestFiltersDefinition, self).setUp()
        self.setup_fixtures()
        context = sgtk.Context(self.tk, project=self.project)
        self.engine = sgtk.platform.start_engine("tk-testengine", self.tk, context)

        # We can't load modules from a test because load_framework can only be called
        # from within a Toolkit bundle or hook, so we'll do it from a hook.
        qt_fw = self.engine.apps["tk-testapp"].frameworks["tk-framework-qtwidgets"]
        su_fw = self.engine.apps["tk-testapp"].frameworks["tk-framework-shotgunutils"]

        # Get a few modules that will be useful later on when instantiating widgets.
        filtering = qt_fw.import_module("filtering")

        # Define the filtering modules as class members for test methods to access
        self.FilterDefinition = filtering.FilterDefinition
        self.FilterItemProxyModel = filtering.FilterItemProxyModel

        # FIXME cannot use patch to mock the shotgun_globals methods because it fails to import the module, so just
        # manually patch the methods used in FilterDefinition
        self.shotgun_globals = su_fw.import_module("shotgun_globals")
        self.shotgun_globals_is_valid_entity_type = (
            self.shotgun_globals.is_valid_entity_type
        )
        self.shotgun_globals_get_type_display_name = (
            self.shotgun_globals.get_type_display_name
        )
        self.shotgun_globals_get_field_display_name = (
            self.shotgun_globals.get_field_display_name
        )
        self.shotgun_globals_get_data_type = self.shotgun_globals.get_data_type
        self.shotgun_globals.is_valid_entity_type = (
            lambda entity_type, project_id: bool(entity_type)
        )
        self.shotgun_globals.get_type_display_name = (
            lambda entity_type, project_id: entity_type
        )
        self.shotgun_globals.get_field_display_name = (
            lambda entity_type, sg_field, project_id: sg_field
        )
        self.shotgun_globals.get_data_type = (
            lambda entity_type, sg_field, project_id: "text"
        )

        # NOTE when using the source/proxy model, the data must be set on the source model, or it will be empty.
        self.source_model = _TestListModel()
        self.proxy_model = self.FilterItemProxyModel()
        self.proxy_model.setSourceModel(self.source_model)

        # Set up a test model with some basic data
        self.string_data = [
            ["row 1"],
            ["row 2"],
            ["some data"],
            ["more data"],
            ["more data"],
            ["more data"],
            ["and more data"],
        ]
        self.number_data = [
            [1],
            [2],
            [33],
            [44444444],
            [1.0],
            [12.34],
        ]
        self.dict_data = [
            [
                {
                    "field_1": 1,
                    "field_2": 2,
                    "field_3": 3,
                }
            ],
            [
                {
                    "field_1": "value 1",
                    "field_2": "value 2",
                    "field_3": "value 3",
                }
            ],
            [
                {
                    "field_1": "value 1",
                    "field_2": "value 2",
                    "field_3": "value 3",
                }
            ],
        ]
        self.object_data = [
            [_TestDataObject(1, "1", True)],
            [_TestDataObject(2, "2", False)],
            [_TestDataObject(1, "2", True)],
            [_TestDataObject(3, "1", False)],
        ]
        self.sg_data = [
            [
                {
                    "type": "Task",
                    "id": 1,
                    "content": "Hello, World",
                    "due_date": 16434533.0,
                    "sg_status_list": "ip",
                }
            ],
            [
                {
                    "type": "Task",
                    "id": 2,
                    "content": "Hello, World",
                    "due_date": 17434533.0,
                    "sg_status_list": "wtg",
                }
            ],
            [
                {
                    "type": "Task",
                    "id": 3,
                    "content": "Hello, World",
                    "due_date": 17434533.0,
                    "sg_status_list": "ip",
                }
            ],
        ]
        self.data_sets = [
            (self.string_data, [None]),
            (self.number_data, [None]),
            (self.dict_data, ["field_1", "field_2", "field_3"]),
            (self.object_data, ["property_1", "property_2", "property_3"]),
            (self.sg_data, ["type", "id", "content", "due_date", "sg_status_list"]),
        ]

    def tearDown(self):
        """
        Destroy the engine and call the base test class to do the rest of the tear down.
        """

        self.engine.destroy()

        self.shotgun_globals.is_valid_entity_type = (
            self.shotgun_globals_is_valid_entity_type
        )
        self.shotgun_globals.get_type_display_name = (
            self.shotgun_globals_get_type_display_name
        )
        self.shotgun_globals.get_field_display_name = (
            self.shotgun_globals_get_field_display_name
        )
        self.shotgun_globals.get_data_type = self.shotgun_globals_get_data_type

        super(TestFiltersDefinition, self).tearDown()

    def test_definitioninition_constructor(self):
        """
        Test the FilterDefinition default constructor.
        """

        fd = self.FilterDefinition()

        assert fd._definition == {}
        assert list(fd.get_fields()) == []

        assert fd.proxy_model is None
        assert fd.get_source_model() is None
        assert fd.filter_roles == [QtCore.Qt.DisplayRole]
        assert fd.ignore_fields == []
        assert fd.use_fully_qualified_name is True
        assert fd.project_id is None
        assert fd.tree_level is None

    def test_property_filter_roles(self):
        """
        Test the 'filter_roles' property.
        """

        fd = self.FilterDefinition()

        # Default instantiation
        assert fd.filter_roles == [QtCore.Qt.DisplayRole]

        # The roles themselves do not matter, just set some data.
        roles = [1, 2, 3]

        # Test the property setter
        fd.filter_roles = roles
        # Test the property getter
        assert fd.filter_roles == roles

    def test_property_ignore_fields(self):
        """
        Test the 'ignore_fields' property.
        """

        fd = self.FilterDefinition()
        assert fd.ignore_fields == []

        fields = [1, 2, 3]
        fd.ignore_fields = fields
        assert fd.ignore_fields == fields

    def test_property_use_fully_qualified_name(self):
        """
        Test the 'use_fully_qualified_name' property.
        """

        fd = self.FilterDefinition()
        assert fd.use_fully_qualified_name is True

        use = False
        fd.use_fully_qualified_name = use
        assert fd.use_fully_qualified_name == use

    def test_property_project_id(self):
        """
        Test the 'project_id' property.
        """

        fd = self.FilterDefinition()
        assert fd.project_id is None

        project_id = self.project["id"]
        fd.use_fully_qualified_name = project_id
        assert fd.use_fully_qualified_name == project_id

    def test_property_tree_level(self):
        """
        Test the 'tree_level' property.
        """

        fd = self.FilterDefinition()
        assert fd.tree_level is None

        level = 5
        fd.use_fully_qualified_name = level
        assert fd.use_fully_qualified_name == level

    def test_properties_proxy_model_and_source_model(self):
        """
        Test the 'proxy_model' and 'source_model' properties together, since the source_model is
        dependent on the proxy_model.
        """

        fd = self.FilterDefinition()
        assert fd.proxy_model is None
        assert fd.get_source_model() is None

        fd.proxy_model = self.proxy_model
        assert fd.proxy_model == self.proxy_model
        assert fd.get_source_model() == self.proxy_model.sourceModel()

        fd.proxy_model = None
        assert fd.proxy_model is None
        assert fd.get_source_model() is None

    # def test_property_fields(self):
    #     """
    #     Test the 'fields' property.
    #     """

    #     fd = self.FilterDefinition()
    #     assert list(fd.get_fields()) == []

    #     # For the 'fields' property, test that the field cannot be set. We'll test this property more
    #     # in later tests that build out the filter definition which will affect the 'fields'.
    #     with pytest.raises(AttributeError):
    #         fd.get_fields = [1, 2, 3]

    def test_staticmethod_get_index_data(self):
        """
        Test the staticmethod 'get_index_data'.
        """

        # No need to create a FilterDefinition object since we're just testing its staticmethod

        for data_set, _ in self.data_sets:
            self.source_model.set_internal_data(data_set)
            role = QtCore.Qt.DisplayRole

            for row in range(self.source_model.rowCount()):
                index = self.source_model.index(row, 0)
                expected_result = index.data(role)
                result = self.FilterDefinition.get_index_data(index, role, None)
                assert result == expected_result

    def test_method_get_field_data(self):
        """
        Test the main 'build' method that (re)initializes the filter definition data.
        """

        fd = self.FilterDefinition()
        assert fd.get_field_data("bad_field_id") == {}

        for data_set, data_set_fields in self.data_sets:
            # FIXME ignore sg data for now
            if "type" in data_set_fields:
                continue

            self.source_model.set_internal_data(data_set)
            fd.proxy_model = self.proxy_model
            fd.build()

            for field in data_set_fields:
                for role in fd.filter_roles:
                    field_id = "{role}.{field}".format(
                        role=role,
                        field=field,
                    )
                    assert fd.get_field_data(field_id) != {}

                    # Still should not have the bad field id
                    assert fd.get_field_data("bad_field_id") == {}

    def test_method_clear(self):
        """
        Test the main 'build' method that (re)initializes the filter definition data.
        """

        fd = self.FilterDefinition()

        for data_set, _ in self.data_sets:
            self.source_model.set_internal_data(data_set)
            fd.proxy_model = self.proxy_model

            fd.build()
            assert fd._definition != {}

            fd.clear()
            assert fd._definition == {}

    def test_method_build_with_no_model(self):
        """
        Test the main 'build' method that (re)initializes the filter definition data.

        Validate it throws an AssertionError if the model has not been set before calling to build.
        """

        fd = self.FilterDefinition()
        assert fd._definition == {}
        assert fd.filter_roles == [QtCore.Qt.DisplayRole]

        fd.build()
        assert fd._definition == {}

    def test_method_build_validate_fields(self):
        """
        Test the main 'build' method that (re)initializes the filter definition data.

        Validate the `field` property after building.
        """

        fd = self.FilterDefinition()

        # Sanity check the initial starting state.
        assert fd._definition == {}
        assert fd.filter_roles == [QtCore.Qt.DisplayRole]

        # Run the test for each data set defined in the Test Class.
        for data_set, data_set_fields in self.data_sets:
            # FIXME ignore sg data for now
            if "type" in data_set_fields:
                continue

            # Set up the model and call build.
            self.source_model.set_internal_data(data_set)
            fd.proxy_model = self.proxy_model
            fd.build()

            for field in data_set_fields:
                # Validate there are the correct number of fields.
                result_fields = list(fd.get_fields())
                assert len(result_fields) == len(fd.filter_roles) * len(data_set_fields)

                # Iterate through the filter roles to ensure we check all the resulting data.
                expected_field_data_keys = set(["name", "type", "values", "data_func"])
                for role in fd.filter_roles:
                    # Validate the expected field id is in the result fields
                    field_id = "{role}.{field}".format(role=role, field=field)
                    assert field_id in result_fields

                    # Validate the field data has the expected keys
                    field_data = fd.get_field_data(field_id)
                    field_data_keys = set(field_data.keys())
                    assert field_data_keys == expected_field_data_keys

    def test_method_build_validate_field_data(self):
        """
        Test the main 'build' method that (re)initializes the filter definition data.

        Validate the `field_data` property after building.
        """

        fd = self.FilterDefinition()
        assert fd._definition == {}
        assert fd.filter_roles == [QtCore.Qt.DisplayRole]

        for data_set, _ in self.data_sets:
            self.source_model.set_internal_data(data_set)
            fd.proxy_model = self.proxy_model
            fd.build()

            model = fd.get_source_model()
            expected_value_keys = set(
                [
                    "name",
                    "value",
                    "count",
                    "icon",
                ]
            )
            for row in range(model.rowCount()):
                index = model.index(row, 0)

                for role in fd.filter_roles:
                    index_data = index.data(role)

                    if isinstance(index_data, dict):
                        for field, value in index_data.items():
                            if index_data.get("type"):
                                # sg data
                                field_id = "{type}.{field}".format(
                                    type=index_data["type"], field=field
                                )
                            else:
                                field_id = "{role}.{field}".format(
                                    role=role, field=field
                                )

                            field_data = fd.get_field_data(field_id)
                            data_values = field_data["values"]

                            # Validate the field value id is in the field values data
                            # value_id = str(value)
                            value_id = "{}.{}".format(field_id, str(value))
                            assert value_id in data_values.keys()

                            # Validate the field values data has the expected dict keys
                            value_data = data_values[value_id]
                            assert set(value_data.keys()) == expected_value_keys

                    elif isinstance(index_data, _TestDataObject):
                        for field, value in vars(index_data.__class__).items():
                            if not isinstance(value, property):
                                continue

                            value = getattr(index_data, field)

                            field_id = "{role}.{field}".format(role=role, field=field)
                            field_data = fd.get_field_data(field_id)
                            data_values = field_data["values"]

                            # Validate the field value id is in the field values data
                            # value_id = str(value)
                            value_id = "{}.{}".format(field_id, str(value))
                            assert value_id in data_values.keys()

                            # Validate the field values data has the expected dict keys
                            value_data = data_values[value_id]
                            assert set(value_data.keys()) == expected_value_keys

                    else:
                        field_id = "{role}.{field}".format(role=role, field=None)
                        data_values = fd.get_field_data(field_id)["values"]

                        # value_id = str(index_data)
                        value_id = "{}.{}".format(field_id, str(index_data))
                        assert value_id in data_values.keys()

                        value_data = data_values[value_id]
                        assert set(value_data.keys()) == expected_value_keys

    def test_method_build_validate_field_value_counts(self):
        """
        Test the main 'build' method that (re)initializes the filter definition data.

        Validate the field value count data.
        """

        fd = self.FilterDefinition()
        assert fd._definition == {}
        assert fd.filter_roles == [QtCore.Qt.DisplayRole]

        for data_set, _ in self.data_sets:
            self.source_model.set_internal_data(data_set)
            fd.proxy_model = self.proxy_model
            fd.build()

            model = fd.get_source_model()
            value_counts = {}
            for row in range(model.rowCount()):
                index = model.index(row, 0)

                for role in fd.filter_roles:
                    index_data = index.data(role)

                    if isinstance(index_data, dict):
                        for field, value in index_data.items():
                            if index_data.get("type"):
                                # sg data
                                field_id = "{type}.{field}".format(
                                    type=index_data["type"], field=field
                                )
                            else:
                                field_id = "{role}.{field}".format(
                                    role=role, field=field
                                )

                            # value_id = str(value)
                            value_id = "{}.{}".format(field_id, str(value))
                            # Keep track of the field value counts to validate after all the
                            # data has been processed
                            value_counts.setdefault(field_id, {}).setdefault(
                                value_id, 0
                            )
                            value_counts[field_id][value_id] += 1

                    elif isinstance(index_data, _TestDataObject):
                        for field, value in vars(index_data.__class__).items():
                            if not isinstance(value, property):
                                continue

                            value = getattr(index_data, field)

                            field_id = "{role}.{field}".format(role=role, field=field)
                            field_data = fd.get_field_data(field_id)
                            data_values = field_data["values"]

                            # Validate the field value id is in the field values data
                            # value_id = str(value)
                            value_id = "{}.{}".format(field_id, str(value))
                            # Keep track of the field value counts to validate after all the
                            # data has been processed
                            value_counts.setdefault(field_id, {}).setdefault(
                                value_id, 0
                            )
                            value_counts[field_id][value_id] += 1

                    else:
                        field_id = "{role}.{field}".format(role=role, field=None)
                        # value_id = str(index_data)
                        value_id = "{}.{}".format(field_id, str(index_data))
                        # Keep track of the field value counts to validate after all the
                        # data has been processed
                        value_counts.setdefault(field_id, {}).setdefault(value_id, 0)
                        value_counts[field_id][value_id] += 1

            # Validate the value counts
            for field_id, field_value_counts in value_counts.items():
                data_values = fd.get_field_data(field_id)["values"]
                for value, count in field_value_counts.items():
                    assert data_values[value]["count"] == count
