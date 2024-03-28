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
    from sgtk.platform.qt import QtCore, QtGui
except:
    # components also use PySide, so make sure  we have this loaded up correctly
    # before starting auto-doc.
    from tank.util.qt_importer import QtImporter

    importer = QtImporter()
    sgtk.platform.qt.QtCore = importer.QtCore
    sgtk.platform.qt.QtGui = importer.QtGui
    from sgtk.platform.qt import QtCore, QtGui

from tank_test.tank_test_base import TankTestBase
from tank_test.tank_test_base import setUpModule  # noqa

from list_model import _TestListModel


class TestFilterMenu(TankTestBase):
    """
    Test the filtering FilterDefinition class.
    """

    def setUp(self):
        """
        Start the test engine, import the necessary frameworks for testing, and initialize some basic model data.
        """

        super(TestFilterMenu, self).setUp()
        self.setup_fixtures()
        context = sgtk.Context(self.tk, project=self.project)
        self.engine = sgtk.platform.start_engine("tk-testengine", self.tk, context)

        # We can't load modules from a test because load_framework can only be called
        # from within a Toolkit bundle or hook, so we'll do it from a hook.
        qt_fw = self.engine.apps["tk-testapp"].frameworks["tk-framework-qtwidgets"]

        # Get a few modules that will be useful later on when instantiating widgets.
        filtering = qt_fw.import_module("filtering")
        search_widget = qt_fw.import_module("search_widget")

        # Define the filtering modules as class members for test methods to access
        self.FilterDefinition = filtering.FilterDefinition
        self.FilterItem = filtering.FilterItem
        self.FilterItemProxyModel = filtering.FilterItemProxyModel
        self.FilterMenu = filtering.FilterMenu
        self.ChoicesFilterItemWidget = filtering.ChoicesFilterItemWidget
        self.SearchFilterItemWidget = filtering.SearchFilterItemWidget
        self.SearchWidget = search_widget.SearchWidget

        model_data = [
            [
                {
                    "number_field": 1,
                    "string_field": "one",
                    "bool_field": True,
                }
            ],
            [
                {
                    "string_field": "two",
                    "bool_field": False,
                }
            ],
            [
                {
                    "number_field": 2,
                    "bool_field": True,
                }
            ],
            [
                {
                    "number_field": 2,
                    "string_field": "two",
                }
            ],
        ]
        self.source_model = _TestListModel()
        self.source_model.set_internal_data(model_data)
        self.proxy_model = self.FilterItemProxyModel()
        self.proxy_model.setSourceModel(self.source_model)

    def tearDown(self):
        """
        Destroy the engine and call the base test class to do the rest of the tear down.
        """

        self.engine.destroy()
        super(TestFilterMenu, self).tearDown()

    def test_filter_menu_constructor(self):
        """
        Test the FilterMenu constructor.
        """

        fm = self.FilterMenu()

        assert isinstance(fm._filters_def, self.FilterDefinition)
        assert fm._filter_groups == {}
        assert fm._proxy_model is None
        assert fm.more_filters_menu is None
        assert isinstance(fm.active_filter, self.FilterItem)
        assert fm.active_filter.filter_type == self.FilterItem.FilterType.GROUP
        assert fm.active_filter.filters == []

    def test_build_menu_with_no_model(self):
        """
        Test the 'initialize_menu' method initializes the static actions as expected.
        """

        fm = self.FilterMenu()
        fm.initialize_menu()

        assert len(fm.actions()) >= 2
        assert fm.actions()[0].text() == "Clear All Filters"
        assert isinstance(fm.more_filters_menu, QtGui.QMenu)

    def test_build_menu_basic(self):
        """
        Test the 'initialize_menu' method initializes the static actions as expected.
        """

        fm = self.FilterMenu()
        fm.set_filter_model(self.proxy_model)
        fm.initialize_menu()

        assert len(fm.actions()) >= 2
        assert fm.actions()[0].text() == "Clear All Filters"
        assert isinstance(fm.more_filters_menu, QtGui.QMenu)

        for field_id in fm._filters_def.get_fields():
            assert field_id in fm._filter_groups

            field_data = fm._filters_def.get_field_data(field_id)
            for filter_id, value_data in field_data["values"].items():
                assert filter_id in fm._filter_groups[field_id].filter_actions
                assert (
                    len(
                        [
                            item
                            for item in fm._filter_groups[field_id].filter_items
                            if item.id == filter_id
                        ]
                    )
                    > 0
                )

                action_widget = (
                    fm._filter_groups[field_id]
                    .filter_actions[filter_id]
                    .defaultWidget()
                )
                assert action_widget.id == filter_id
                assert action_widget.group_id == field_id

    def test_clear_menu(self):
        """
        Test the 'initialize_menu' method initializes the static actions as expected.
        """

        fm = self.FilterMenu()
        fm.set_filter_model(self.proxy_model)
        fm.initialize_menu()
        assert len(fm.actions()) > 0
        assert fm._filter_groups != {}
        assert fm._filters_def._definition != {}
        assert fm.more_filters_menu is not None

        fm.clear_menu()
        assert fm.actions() == []
        assert fm._filter_groups == {}
        assert fm._filters_def._definition == {}
        assert fm.more_filters_menu.isEmpty()

    def test_action_triggered(self):
        """
        Test the menu action trigger slot.
        """

        fm = self.FilterMenu()
        fm.set_filter_model(self.proxy_model)
        fm.initialize_menu()

        field_id = "{}.number_field".format(fm._filters_def.filter_roles[0])
        filter_item = fm._filter_groups[field_id].filter_items[0]

        action = fm._filter_groups[field_id].filter_actions[filter_item.id]
        widget = action.defaultWidget()

        assert not action.isChecked()
        assert isinstance(widget, self.ChoicesFilterItemWidget)
        assert not widget.has_value()

        action.trigger()

        assert action.isChecked()
        assert widget.has_value()

        action.trigger()

        assert not action.isChecked()
        assert not widget.has_value()

    def test_clear_filters(self):
        """
        Test the 'clear_filters' method after setting a single filter.
        """

        fm = self.FilterMenu()
        fm.set_filter_model(self.proxy_model)
        fm.initialize_menu()

        field_id = "{}.number_field".format(fm._filters_def.filter_roles[0])
        filter_item = fm._filter_groups[field_id].filter_items[0]

        action = fm._filter_groups[field_id].filter_actions[filter_item.id]
        widget = action.defaultWidget()
        # Sanity check the filter item widget
        assert isinstance(widget, self.ChoicesFilterItemWidget)

        action.trigger()

        assert action.isChecked()
        assert widget.has_value()

        fm.clear_filters()
        assert not action.isChecked()
        assert not widget.has_value()

    def test_clear_all_filters(self):
        """
        Test the 'clear_filters' method after setting all filters.
        """

        fm = self.FilterMenu()
        fm.set_filter_model(self.proxy_model)
        fm.initialize_menu()

        for filter_group in fm._filter_groups.values():
            for filter_action in filter_group.filter_actions.values():
                widget = filter_action.defaultWidget()

                if isinstance(widget, self.ChoicesFilterItemWidget):
                    filter_action.trigger()

                    assert filter_action.isChecked()
                    assert widget.has_value()

                elif isinstance(widget, self.SearchFilterItemWidget) and isinstance(
                    widget.line_edit, self.SearchWidget
                ):
                    widget.line_edit._set_search_text("dummy value")
                    assert widget.has_value()

                else:
                    assert False, "Unkown filter item widget class"

        fm.clear_filters()
        for filter_group in fm._filter_groups.values():
            for filter_action in filter_group.filter_actions.values():
                widget = filter_action.defaultWidget()
                assert not widget.has_value()
                assert not filter_action.isChecked()

    def test_get_current_filters(self):
        """
        Test the 'clear_filters' method after setting a single filter.
        """

        fm = self.FilterMenu()
        fm.set_filter_model(self.proxy_model)
        fm.initialize_menu()

        field_id = "{}.number_field".format(fm._filters_def.filter_roles[0])
        filter_item = fm._filter_groups[field_id].filter_items[0]
        action = fm._filter_groups[field_id].filter_actions[filter_item.id]
        # Sanity check the filter item widget
        assert isinstance(action.defaultWidget(), self.ChoicesFilterItemWidget)

        # Trigger the action to set the value for this filter item.
        action.trigger()

        result_filters = fm.get_current_filters()
        assert len(result_filters) == 1

        group_filter_item = result_filters[0]
        assert isinstance(group_filter_item, self.FilterItem)
        assert group_filter_item.filter_type == self.FilterItem.FilterType.GROUP
        assert group_filter_item.filter_op == self.FilterItem.FilterOp.OR
        assert len(group_filter_item.filters) == 1

        result_filter_item = group_filter_item.filters[0]
        assert result_filter_item.id == filter_item.id
        assert result_filter_item.filter_type == filter_item.filter_type
        assert result_filter_item.filter_op == filter_item.filter_op
        assert result_filter_item.filter_value == filter_item.filter_value

    def test_get_current_filters_exclude(self):
        """
        Test the 'clear_filters' method after setting a single filter.
        """

        fm = self.FilterMenu()
        fm.set_filter_model(self.proxy_model)
        fm.initialize_menu()

        field_id = "{}.number_field".format(fm._filters_def.filter_roles[0])
        filter_item = fm._filter_groups[field_id].filter_items[0]
        action = fm._filter_groups[field_id].filter_actions[filter_item.id]
        # Sanity check the filter item widget
        assert isinstance(action.defaultWidget(), self.ChoicesFilterItemWidget)

        # Trigger the action to set the value for this filter item.
        action.trigger()

        result_filters = fm.get_current_filters(exclude_choices_from_fields=[field_id])
        assert len(result_filters) == 0

    def test_get_search_filter_item_and_field_id(self):
        """Test the '_get_search_filter_item_id' and '_get_search_filter_field_id' methods."""

        fm = self.FilterMenu()

        # Parametrize the filter group id (cannot use pytest.mark.parametrize inside TankTestBase)
        filter_group_ids = [
            "123.filter_group_name",
            "999.primary_entity.LinkedEntityType.entity_field",
        ]
        for filter_group_id in filter_group_ids:
            # Generate the id for the search filter widget
            search_filter_widget_id = fm._get_search_filter_item_id(filter_group_id)

            # Create the search filter widget
            sw = self.SearchFilterItemWidget(
                search_filter_widget_id,
                filter_group_id,
                {},
            )

            # Now test that we can get the filter group id back from the search widget
            search_filter_field_id = fm._get_search_filter_field_id(sw.id)
            assert search_filter_field_id == filter_group_id
