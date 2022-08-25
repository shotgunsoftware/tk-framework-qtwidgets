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

from .filter_definition import FilterMenuFiltersDefinition
from .filter_item import FilterItem
from .filter_item_widget import (
    ChoicesFilterItemWidget,
    TextFilterItemWidget,
)
from .filter_menu_group import FilterMenuGroup

shotgun_menus = sgtk.platform.current_bundle().import_module("shotgun_menus")

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_model"
)
ShotgunModel = shotgun_model.ShotgunModel


class NoCloseOnActionTriggerShotgunMenu(shotgun_menus.ShotgunMenu):
    """
    ShotgunMenu subclass that prevents the menu from closing when an action is triggered.
    """

    def mouseReleaseEvent(self, event):
        """
        Override the QMenu method.

        This is a trick to preventing the menu from closing when one of its actions are triggered.

        :param event: The QT mouse event
        :type event: :class:`sgtk.platform.qt.QtGui.QMouseEvent`
        """

        action = self.activeAction()
        if action and action.isEnabled():
            action.setEnabled(False)
            super(NoCloseOnActionTriggerShotgunMenu, self).mouseReleaseEvent(event)
            action.setEnabled(True)
            action.trigger()
        else:
            super(NoCloseOnActionTriggerShotgunMenu, self).mouseReleaseEvent(event)


class FilterMenu(NoCloseOnActionTriggerShotgunMenu):
    """
    A menu that provides filtering functionality.

    How the menu's filter options are built:
        A QSortFilterProxyModel is set for the menu, and the filter menu options reflect the data
        in the model. The menu's FilterDefinition processes the model data and constructs a dictionary
        of data that contains the filter data for each of the model items. The FilterDefintion is then
        used to populate the menu with the filter QAction/QWidgetAction items.

    When the menu is updated/refreshed:
        The filter menu is refreshed based on the current model data on showing the menu, to ensure
        the filter options reflect the current model data accurately. The menu is also refreshed
        when the filter options are modified, which changes the model data. The menu may also be
        forced to be refreshed on calling the `refresh` method with param `force` as True.

    Example usage::

        # Create the menu
        filter_menu = FilterMenu(parent)

        # Set the proxy model that contains the data to be filtered on. This must be called
        # before the menu is initialized since the menu requires a model to build the filter
        # items (if there is no model, there will be no filter options. The proxy model must
        # inherit from the QSortFilterProxyModel class.
        #
        # If 'connect_signals' is True, the filter model is also expected to have the method
        # 'set_filter_items'; the FilterItemProxyModel and FilterItemTreeProxyModel classes
        # implement this method, and are designed to work with this FilterMenu class.
        #
        # If `connect_signals` is not True, the caller will need to connect to the signal
        # `filters_changed` signal, which the menu emits, when filters have been modified and
        # the proxy model requires updating.
        filter_menu.set_filter_model(proxy_model, connect_signals=True)

        # Initialize the menu. This will clear the menu and set up the static menu actions (e.g.
        # "Clear Filters", "More Filters") and refresh the menu to display available filter
        # options (if the model has any data loaded).
        filter_menu.initialize_menu()

        # Create a QToolButton and set the filter menu on it. The FilterMenuButton class is not
        # required, any QToolButton class may be used. The benefit of the FilterMenuButton class
        # is that it is designed to work with the FilterMenu specfically, for example, the icon
        # will be updated when the menu has active filtering to visually indicate the data is
        # filtered.
        filter_button = FilterMenuButton(parent)
        filter_button.setMenu(filter_menu)

    Optional::

        # By default, the filter menu options are built from the menu's model data, and the
        # model item data role, QtCore.Qt.DisplayRole, is used to extract the data from the model.
        # This can be overriden by using `set_filter_roles` and providing a new list of roles
        # that will be used to extract the model data.
        self._filter_menu.set_filter_roles(
            [
                QtCore.Qt.DisplayRole,
                filter_menu.proxy_model.SOME_ITEM_DATA_ROLE,
                ...
            ]
        )

        # Call `set_ignore_fields` to ignore certain data when building the filters.
        filter_menu.set_ignore_fields(
            [
                "{ROLE}.{FIELD_NAME},  # For non SG data, fields are of the format "role.field", e.g. "QtCore.Qt.DisplayRole.name"
                "{SG_ENTITY_TYPE}.{FIELD_NAME}",  # For SG data, fields are of the format "entity_type.field", e.g. "Task.code"
            ]
        )

    """

    # Signal emitted when the filters have changed by modifying the menu options/actions.
    filters_changed = QtCore.Signal()
    # Signal emitted when menu is about to refresh
    menu_about_to_be_refreshed = QtCore.Signal()
    # Signal emitted when menu is finished refreshing
    menu_refreshed = QtCore.Signal()

    def __init__(self, parent=None):
        """
        Constructor

        :param parent: The parent widget.
        :type parent: :class:`sgtk.platform.qt.QtWidget`
        """

        super(FilterMenu, self).__init__(parent)

        # The filters definitions that are built based on the current model data, and which are used
        # to build the filter menu UI.
        self._filters_def = FilterMenuFiltersDefinition(self)

        # Set the project id for the filters definition to allow handling SG data.
        bundle = sgtk.platform.current_bundle()
        if bundle.tank.pipeline_configuration.is_site_configuration():
            self._filters_def.project_id = None
        else:
            self._filters_def.project_id = (
                bundle.tank.pipeline_configuration.get_project_id()
            )

        # A mapping of field id (group) to list of FilterMenuGroup objects.
        self._filter_groups = {}
        # A mapping of field id to whether or not that group of filters is visible.
        self._field_visibility = {}

        # A submenu to show/hide filter field groups.
        self._more_filters_menu = None

        # The filter model and its source model, that the filters in this menu are built bsaed on.
        self._proxy_model = None
        self._source_model = None

        # Flag indicating the the menu is currently being refreshed
        self._is_refreshing = False
        # Flag indicating that the menu triggered a refresh through a model layoutChanged signal
        self._menu_triggered_refresh = False

        # Connect signals/slots
        self.aboutToShow.connect(self._about_to_show)

        # Initialize the active filter as an AND group filter item, where filter items will be added
        # based on menu selection.
        self._active_filter = FilterItem.create_group(FilterItem.FilterOp.AND)

    @property
    def active_filter(self):
        """
        Get the current active filters that are set within the menu.
        """
        return self._active_filter

    @property
    def has_filtering(self):
        """
        Get whether or not the menu has any active filtering.
        """
        return bool(self._active_filter and self._active_filter.filters)

    @staticmethod
    def set_widget_action_default_widget_value(widget_action, checked):
        """
        Convenience method to set the QWidgetAction's default widget's value to the checked value
        of the QWidgetAction.

        This is mainly used by the QWidgetAction's triggered callback to handle different
        triggered signal signatures between Qt versions.
        """

        widget_action.defaultWidget().set_value(widget_action.isChecked())

    #############################################@##################################################
    # Public methods
    #############################################@##################################################

    def set_visible_fields(self, fields):
        """
        Set the filters that belong to any of the given fields to be visible.

        :param fields: The filters within the given fields will be shown.
        :type fields: list<str>
        """

        if not fields:
            return

        for field in fields:
            self._field_visibility[field] = True

    def set_accept_fields(self, fields):
        """
        Set the fields to ignore when building the filter definition for the menu.

        :param fields: The fields to ignore
        :type fields: list<str>
        """

        self._filters_def.accept_fields = fields

    def set_ignore_fields(self, fields):
        """
        Set the fields to ignore when building the filter definition for the menu.

        :param fields: The fields to ignore
        :type fields: list<str>
        """

        self._filters_def.ignore_fields = fields

    def set_use_fully_qualifiied_name(self, use):
        """
        Set the flag to use the fully qualified name for filters. For example, a filter item
        representing SG data will prefix the filter name with the entity type.

        :param use: True will show fully qualified names for filters.
        :type use: bool
        """

        self._filters_def.use_fully_qualified_name = use

    def set_filter_roles(self, roles):
        """
        Set the list of model item data roles that are used to extract data from the model, in
        order to build the menu filters.
        """

        self._filters_def.filter_roles = roles

    def set_tree_level(self, level):
        """
        Set the model tree index level which the filters will be built from. This is to handle
        tree models that defer loading data, set this to the expected leaf node level.
        """

        self._filters_def.tree_level = level

    def save_state(self):
        """
        Return a dictionary describing the current menu filter state. This can be used to save
        and restore the menu state.
        """

        state = {}

        for field_id, visible in self._field_visibility.items():
            if not visible:
                # We're only concerned with the visible fields
                continue

            state.setdefault(field_id, {})
            filter_items = self._get_filter_group_items(field_id)

            for filter_item in filter_items:
                action = self._get_filter_group_action(field_id, filter_item.id)
                widget = action.defaultWidget()
                if widget.has_value():
                    state[field_id][filter_item.id] = widget.value

        return state

    def restore_state(self, state):
        """
        Restore the menu to the given state.

        :param state: The menu state to restore.
        :type state: dict

        e.g.::

            state = {
                "field_id_1": {
                    "filter_id_1": "filter_id_1_value",
                    "filter_id_2": "filter_id_2_value",
                },
                "field_id_2": {
                    "filter_id_3": "filter_id_3_value",
                    "filter_id_4": "filter_id_4_value",
                },
                ...
            }

        """

        updated = False

        for field_id, filter_items in state.items():
            if field_id not in self._filter_groups:
                continue

            filter_group = self._filter_groups[field_id]

            if not self._field_visibility.get(field_id, False):
                filter_group.show_hide_action.trigger()

            for filter_id, value in filter_items.items():
                action = filter_group.filter_actions.get(filter_id)
                if action:
                    self.blockSignals(True)
                    try:
                        action.defaultWidget().value = value
                        filter_group.show_action(action)
                        updated = True
                    finally:
                        self.blockSignals(False)

        if updated:
            self._emit_filters_changed()

    def set_filter_model(self, filter_model, connect_signals=True):
        """
        Set the source and proxy models that define the filter menu options.

        :param filter_model: The model that is used to build the menu filters.
        :type filter_model: :class:`sgtk.platform.qt.QSortFilterProxyModel`
        :param connect_signals: Whether or not to connect model signals to
                                the appropriate filter menu methods; e.g. model
                                layoutChanged will rebuild the menu.
        :type connect_signals: bool
        """

        assert hasattr(
            filter_model, "sourceModel"
        ), "Filter model must be a subclass of QSortFilterProxyModel"

        if self._proxy_model:
            try:
                self._proxy_model.layoutChanged.disconnect()
                self.filters_changed.disconnect(self._update_filter_model_cb)
            except RuntimeError:
                # Signals were never connected
                pass

        self._proxy_model = filter_model
        self._source_model = filter_model.sourceModel()
        self._filters_def.proxy_model = self._proxy_model

        try:
            # Attempt to disable the HierarchicalFilteringProxyModel caching mechanism, this caching
            # mechanism does not play nice with the filter menu.
            # TODO make the filter menu work with the caching mechanism
            self._proxy_model.enable_caching(False)
        except AttributeError:
            # This proxy model does not have a the caching mechanism we want to disable, continue on.
            pass

        if connect_signals:
            self._proxy_model.layoutChanged.connect(self.refresh)

            # Sanity check for faster debugging. The filter model is expected to have the method 'set_filter_items'
            # when connecting the slot '_update_filter_model_cb'.
            assert hasattr(
                filter_model, "set_filter_items"
            ), "Expected filter model to have attribute `set_filter_items`"
            self.filters_changed.connect(self._update_filter_model_cb)

            # TODO enable signal/slot connection for smarter menu update
            # self.source_model.rowsInserted.connect(self._insert_filters)
            # self.source_model.rowsRemoved.connect(self._remove_filters)
            # self.source_model.dataChanged.connect(self._update_filters)

    def refresh(self, force=False):
        """
        Rebuild the FilterDefinition from the current model data and update the menu with the
        new filter definition.

        TODO: bulid the filter definition async - performance starts to degrade at ~400 model items.
        """

        if self._is_refreshing:
            return

        # Allow refresh if the filter menu itself called the refresh slot directly, or triggered the
        # refresh via signal/slot. Until we have async refresh, this is to avoid the model signals
        # (like layoutChanged) from hammering the refresh on each model data change.
        # If an outside caller requires a refresh, pass the force flag as True.
        if not force and self.sender() is not None and self.sender() != self:
            if not self._menu_triggered_refresh:
                return

            self._menu_triggered_refresh = False

        # Emit signal about to refresh and set the flag to avoid recursive refreshing.
        self.menu_about_to_be_refreshed.emit()
        self._is_refreshing = True

        self._filters_def.build()
        self._refresh_menu()

        # Done - unset the refresh flag and emit signal
        self._is_refreshing = False
        self.menu_refreshed.emit()

    def clear_menu(self):
        """
        Clear any active filters that are set in the menu. Clear the internal menu data and
        remove all items from the menu.
        """

        # First clear any filter values set in the menu.
        self.clear_filters()

        # Reset the internal menu data members
        self._filter_groups = {}
        self._filters_def.clear()

        # Clear the menu widgets
        self.clear()
        self._more_filters_menu = None

    def clear_filters(self):
        """
        Clear any active filtesr that are set in the menu.
        """

        # Do not trigger any signals while clearing the filters.
        self.blockSignals(True)

        # Only emit a change if the menu actually had active filters.
        had_value = False

        try:
            for filter_group in self._filter_groups.values():
                for action in filter_group.filter_actions.values():
                    filter_item_widget = action.defaultWidget()
                    if action.isChecked() or filter_item_widget.has_value():
                        had_value = True

                    # Uncheck the QAction.
                    action.setChecked(False)
                    # Clear the value from the FilterItemWidget.
                    filter_item_widget.clear_value()
        finally:
            # Ensure the signals are unblocked.
            self.blockSignals(False)

        if had_value:
            # Clear the active filter and emit the changed signal.
            self._active_filter.filters = []
            self.filters_changed.emit()

    def get_current_filters(self, exclude_fields=None):
        """
        Return the list of FilterItem objects that represent the current filtering
        applied from the menu. Filters will be omitted that belong to the excluded
        fields list given.

        The result will be a list of FilterItem Groups that OR the filters within
        each group.

        :param exclude_fields: The list of fields to exclude when collecting the
                               currently active filtering from the menu.
        :type exclude_fields: list<str>

        :return: The current filters, excluding the given fields.
        :rtype: list<FilterItem>
        """

        current_filters = []

        # Iterate over the filter items by field group
        for field_id, filter_group in self._filter_groups.items():
            if exclude_fields is not None and field_id in exclude_fields:
                continue

            # Get the filter items that are active (e.g. have a value set).
            active_filters = [
                filter_item
                for filter_item in filter_group.filter_items
                if self._get_filter_group_action(field_id, filter_item.id)
                .defaultWidget()
                .has_value()
            ]

            if active_filters:
                # Add a FilterItem that will OR all of the filter items within the field together.
                current_filters.append(
                    FilterItem.create_group(
                        FilterItem.FilterOp.OR, group_filters=active_filters
                    )
                )

        return current_filters

    def initialize_menu(self):
        """
        Initialize the filter menu.
        """

        # First reset and clear the menu.
        self.clear_menu()

        # Add the static menu actions
        clear_action = self.addAction("Clear All Filters")
        clear_action.triggered.connect(self.clear_filters)

        # Build and add the configuration menu as a submenu to the main filter menu.
        self._more_filters_menu = NoCloseOnActionTriggerShotgunMenu(self)
        self._more_filters_menu.setTitle("More Filters")
        self.addMenu(self._more_filters_menu)

        self.addSeparator()

        # Build the FilterDefinition and add the filter items based on the definition.
        self.refresh()

        # If any filters were set during initialization, update the active filter and emit a signal
        # for the model to update accordingly.
        if self.has_filtering:
            self._emit_filters_changed()

    #############################################@##################################################
    # Protected methods
    #############################################@##################################################

    @sgtk.LogManager.log_timing
    def _refresh_menu(self, field_ids=None):
        """
        Update the menu based on the current FilterDefinition.

        Iterate through the filter items by field group:
            - Filter item field groups will be removed as a whole, if the current FilterDefinition
              does have a record of the field.
            - Individual filter items will be removed, if the FilterDefinition no longer has a
              record of it.
            - Filter item counts will be updated according to the current FilterDefinition
            - Individual filter items will be added, if the field it belongs to already exists
            - Filter item field groups will be added, if no field exists yet

        :param field_ids: The menu group fields to update.
        :type field_ids: list<str>
        """

        if self.isEmpty():
            # The menu has nothing in it, just build it.
            self.initialize_menu()
            return

        field_ids = field_ids or []

        for field_id, filter_group in self._filter_groups.items():
            if field_ids and not field_id in field_ids:
                continue

            if not self._field_visibility.get(field_id, False):
                # Skip hidden filters
                continue

            data = self._filters_def.get_field_data(field_id)
            if not data:
                # The field group no longer exists, remove the whole group.
                self._remove_filter_groups(field_id)
                continue

            # The current field data to update the current menu state.
            updated_field_data = self._filters_def.get_field_data(field_id)
            updated_filters_values = updated_field_data.get("values", {})

            # Update existing filter item widget counts
            existing_value_ids = []
            # Copy the filter items since we may be removing some items as we go.
            # current_filter_items = list(filter_items)
            current_filter_items = list(filter_group.filter_items)
            for item in current_filter_items:
                action = self._get_filter_group_action(field_id, item.id)
                if not isinstance(action.defaultWidget(), ChoicesFilterItemWidget):
                    # Only ChoicesFilterItemWidgets need updating
                    continue

                existing_value_ids.append(item.id)
                filter_value = updated_filters_values.get(item.id)
                if filter_value is not None:
                    # Update the widget count label
                    action.defaultWidget().set_value(filter_value)
                else:
                    # Filter item no longer has any values, remove it
                    self._remove_filter_action(field_id, item)

            # For string filter data types, a search widget will be added to the top of the list of choices.
            # The search widget will be removed when the whole group is removed. When the group exists but
            # has no existing items, this is our hint to add the search widget back.
            if (
                not filter_group.filter_items
                and updated_field_data["type"] == FilterItem.FilterType.STR
            ):
                filter_id = self._get_search_filter_item_id(field_id)
                filter_item, filter_action = self._create_filter_item_and_action(
                    field_id, updated_field_data, filter_id
                )
                filter_group.insert_into_menu(self, filter_item, filter_action)

            # Insert any new filter items into an existing group.
            for value_id, value_data in updated_filters_values.items():
                if value_id in existing_value_ids:
                    continue

                filter_item, filter_action = self._create_filter_item_and_action(
                    field_id, data, value_id, value_data
                )
                filter_group.insert_into_menu(self, filter_item, filter_action)

        # Add any new filter field groups in sorted order
        sorted_field_ids = self._filters_def.get_fields(sort=True)
        self._add_filter_groups(sorted_field_ids)

        # The menu layout may have changd, ensure it is positioned nicely.
        self._adjust_position()

    def _add_filter_groups(self, field_ids, ignore_existing=True):
        """
        Add new filter group to the menu for the given fields. If the field group already exists,
        it will ignore that field.

        :param field_ids: The fields to add filters for.
        :type field_ids: list<str>
        :param ignore_existing: Only add new fields to the menu, ignore fields that already exist.
        :type ignore_existing: bool
        """

        for field_id in field_ids:
            if ignore_existing and field_id in self._filter_groups:
                # Skip the field, it already exists.
                continue

            # Get the field filter data to build the filter item actions.
            field_data = self._filters_def.get_field_data(field_id)
            filter_item_and_actions = []
            if field_data["type"] == FilterItem.FilterType.STR:
                # Create a text search filter item. TODO allow search bar for any data type
                filter_id = self._get_search_filter_item_id(field_id)
                filter_item_and_actions.append(
                    self._create_filter_item_and_action(field_id, field_data, filter_id)
                )
            # Create filter items for list of value choices
            filter_values = field_data.get("values", {})
            for filter_id, filter_value in filter_values.items():
                filter_item_and_actions.append(
                    self._create_filter_item_and_action(
                        field_id, field_data, filter_id, filter_value
                    )
                )

            # Create the filter group object to manage this grouping, and add the filter item and actions.
            # Set the maximum initial number of items shown per group to 5, more item may be shown as user
            # requests to show more.
            filter_group = FilterMenuGroup(field_id, show_limit_increment=5)
            filter_group.add_to_menu(self, filter_item_and_actions, field_data["name"])

            # Update "More Filters" to include the newly added filter gorup.
            self._add_action_to_more_filters_menu(filter_group, field_data["name"])

            # Lastly, keep track of the filter group object by its id
            self._filter_groups[field_id] = filter_group

    def _create_filter_item_and_action(
        self, field_id, field_data, filter_id, filter_value=None
    ):
        """
        Create a FilterItem object and its corresponding FilterItemWidget.

        Keep track of the FilterItem and QWidgetAction objects in the internal
        `_filter_groups` dict by field and filter id.

        :param field_id: The field group this filter belongs to.
        :type field_id: str
        :param field_ata: The field's data used to create the filter action.
        ;type field_data: dict
        :param filter_id: The filter id for the filter action to be created.
        :type filter_id: str
        :param filter_value: The value for the filter to be created.
        :type filter_value: any

        :return: The created filter item and its corresponding action.
        :rtype: (FilterItem, QAction)
        """

        filter_item_data = {
            "filter_role": field_data.get("filter_role"),
            "data_func": field_data.get("data_func"),
        }

        if filter_value:
            filter_widget_class = ChoicesFilterItemWidget
            filter_item_data.update(
                {
                    "filter_type": field_data["type"],
                    "filter_op": FilterItem.default_op_for_type(field_data["type"]),
                    "filter_value": filter_value.get("value"),
                    "display_name": filter_value.get("name", str(filter_id)),
                    "count": filter_value.get("count", 0),
                    "icon": filter_value.get("icon"),
                }
            )
        else:
            filter_widget_class = TextFilterItemWidget
            filter_item_data["filter_type"] = FilterItem.FilterType.STR
            filter_item_data["filter_op"] = FilterItem.FilterOp.IN

        filter_item = FilterItem.create(filter_id, filter_item_data)
        action = self._create_filter_action_widget(
            filter_item, field_id, filter_item_data, filter_widget_class
        )

        return (filter_item, action)

    def _create_filter_action_widget(
        self, filter_item, field_id, filter_data, widget_class
    ):
        """
        Create the FilterItemWidget for the given FilterItem. A QWidgetAction is
        also created to manage the FilterItemWidget and allow it to be added to
        the menu.

        :param filter_item: The FilterItem this widget corresponds to.
        :type filter_item: FilterItem
        :param field_id: The field the filter item belongs to.
        :type field_id: str
        :param filter_data: The filter's data to create the widget with.
        :type filter_data: dict
        :param widget_class: The specific FilterItemWidget class to create
                             the new widget.
        :type widget_class: FilterItemWidget class or subclass

        :return: The QWidgetAaction object that has the FilterItemWidget set as
                 its default widget.
        :rtype: :class:`sgtk.platform.qt.QWidgetAction`
        """

        widget_action = QtGui.QWidgetAction(None)
        widget = widget_class(filter_item.id, field_id, filter_data)
        widget.state_changed.connect(
            lambda state, a=widget_action: self._filter_widget_checked(a, state)
        )
        widget.value_changed.connect(
            lambda text, f=filter_item: self._filter_widget_value_changed(f, text)
        )

        widget_action.setDefaultWidget(widget)
        widget_action.setCheckable(True)

        widget_action.triggered.connect(
            lambda checked=None, a=widget_action: self.set_widget_action_default_widget_value(
                a, checked
            )
        )

        return widget_action

    def _remove_filter_groups(self, field_ids):
        """
        Remove all filter items for each field group given.

        :param field_ids: The field groups for remove all actions from the menu.
        :type field_ids: list<str>
        """

        if not isinstance(field_ids, list):
            field_ids = [field_ids]

        for field_id in field_ids:
            # Operate on a copy of the filter items since _remove_filter_action will modify the
            # list of filter items when items are removed.
            filter_items = list(self._get_filter_group_items(field_id))
            for filter_item in filter_items:
                self._remove_filter_action(field_id, filter_item)

    def _remove_filter_action(self, field_id, filter_item):
        """
        Remove an individual filter action from the menu corresponding to the field and filter
        item object.

        The action will be removed from the menu, as well as the internal menu member
        `_filter_groups` will be updated to remove the action.

        :param field_id: The field group the action belongs to.
        :type field_id: str
        :param filter_item: The FilterItem the action corresponds to.
        :type filter_item: FilterItem
        """

        action = self._get_filter_group_action(field_id, filter_item.id)

        if action.defaultWidget().has_value():
            # Do not remove a filter if it has a value

            if isinstance(action.defaultWidget(), ChoicesFilterItemWidget):
                # Reset count to 0 for choices filter widgets
                action.defaultWidget().set_value({"count": 0})

            return

        self._filter_groups[field_id].remove_item(filter_item)
        self.removeAction(action)

    def _add_action_to_more_filters_menu(self, filter_group, field_name):
        """
        Add a new action to the `_more_filters_menu` for the given field. The "More Filter Menu"
        is used to show/hide filter field groups.

        :param field_id: The field the new action corresponds to
        :type field_id: str
        :param field_name: The display name for the action in the menu
        :param field_name: str
        """

        assert self._more_filters_menu, "'More Filters' menu not initialized"
        if not self._more_filters_menu:
            return

        field_id = filter_group.group_id
        filter_id = "{}.MoreFilters".format(field_id)
        filter_widget = ChoicesFilterItemWidget(
            filter_id,
            field_id,
            {
                "display_name": field_name,
            },
        )

        action = QtGui.QWidgetAction(self._more_filters_menu)
        action.setCheckable(True)
        action.setDefaultWidget(filter_widget)

        action.triggered.connect(
            lambda checked=None, a=action: self.set_widget_action_default_widget_value(
                a, checked
            )
        )

        filter_group.show_hide_action = action

        checked = self._field_visibility.get(field_id, False)
        filter_widget.set_value(checked)
        filter_group.set_visible(checked)

        # Connect this signal/slot after setting the fitler widget value to avoid triggering it.
        filter_widget.state_changed.connect(
            lambda state, a=action: self._toggle_filter_group(a, state)
        )

        # Add the new action and then move it into alphabetical order.
        self._more_filters_menu.addAction(action)
        more_filters_actions = sorted(
            self._more_filters_menu.actions(),
            key=lambda a: a.defaultWidget().name,
        )
        action_index = more_filters_actions.index(action)
        if action_index + 1 < len(more_filters_actions):
            insert_before_action = more_filters_actions[action_index + 1]
            self._more_filters_menu.insertAction(insert_before_action, action)

    def _emit_filters_changed(self):
        """
        Update the active filter and emit a signal that the filters have changed.
        """

        self._active_filter.filters = self.get_current_filters()
        self.filters_changed.emit()

    def _get_search_filter_item_id(self, field_id):
        """
        Convenience method to ensure the same filter id is used for text search filter item widgets.

        :param field_id: The field group that the search filter item widget belongs to.
        :type field_id: str

        :return: The id for the search filter item widget.
        :rtype: str
        """

        # There should only be one TextFilterItemWidget per field group, which makes
        # it safe to use the widget class name as part of the id.
        return "{}.{}".format(field_id, "TextFilterItemWidget")

    def _get_filter_group_items(self, field_id):
        """
        Convenience method to get all filter items for a given group.

        :param field_id: The field group to get the items from.
        :type field_id: str

        :return: The filter group's items
        :rtype: list<FilterItem>
        """

        return self._filter_groups[field_id].filter_items

    def _get_filter_group_action(self, field_id, filter_id):
        """
        Convenience method to get an action from a filter group.

        :param field_id: The field group to get the action from.
        :type field_id: str

        :return: The filter group's action.
        :rtype: QAction
        """

        if field_id not in self._filter_groups:
            return None

        return self._filter_groups[field_id].filter_actions.get(filter_id)

    def _adjust_position(self):
        """
        Adjust the menu to ensure all actions are visible.
        """

        sz = self.sizeHint()
        desktop = QtGui.QApplication.desktop()
        geom = desktop.availableGeometry(self)
        available_height = geom.height() - self.y()

        if sz.height() > available_height:
            adjust_y = max(0, geom.bottom() - sz.height())
            self.setGeometry(self.x(), adjust_y, sz.width(), sz.height())

    ################################################################################################
    # Callbacks
    ################################################################################################

    def _about_to_show(self):
        """
        Callback triggered when the menu is about to show.
        """

        # For now, we will just refresh the menu any time it is opened. This is a quick brute force
        # solution to ensuring that the filter menu items are up to date with the current state of
        # the model.
        # TODO connect to model signals rowsInserted/rowsRemoved/dataChanged and update the menu
        # according to the updated indexes
        self.refresh()

    def _update_filter_model_cb(self):
        """
        Update the filter model to reflect the current filtering set based on the menu.
        """

        if self._proxy_model:
            self._menu_triggered_refresh = True
            self._proxy_model.set_filter_items([self.active_filter])

    def _toggle_filter_group(self, action, state):
        """
        Show or hide the actions corresponding to the widget that was toggled to show/hide filter groups.
        """

        action.setChecked(state == QtCore.Qt.Checked)
        widget = action.defaultWidget()
        checked = widget.has_value()
        field_id = widget.group_id

        # Keep track of the field group visibility.
        self._field_visibility[field_id] = checked
        self._filter_groups[field_id].set_visible(checked)

        # Ensure the filter group items are up to date with the current menu filters.
        self._refresh_menu([field_id])

        # Adjust menu position after removing actions that may have altered the menu layout.
        self._adjust_position()

    def _filter_widget_checked(self, action, state):
        """
        Callback triggered when a FilterItemWidget `state_changed` signal emitted.

        :param action: The menu action associated with the filter widget.
        :type action: :class:`sgtk.platform.qt.QtGui.QAction`
        :param state: The filter widget's checkbox state.
        :type state: :class:`sgtk.platform.qt.QtCore.Qt.CheckState`
        """

        # Keep the parent QAction checked state in sync with the filter item widget's checkbox state.
        action.setChecked(state == QtCore.Qt.Checked)
        self._emit_filters_changed()

    def _filter_widget_value_changed(self, filter_item, text):
        """
        Callback triggered when a FilterItemWidget `value_changed` signal emitted.

        :param filter_item: The FilterItem assoicated with the filter widget.
        :type filter_item: FilterItem
        :param text: The new text value the filter widget has.
        :type text: str
        """

        filter_item.filter_value = text
        self._emit_filters_changed()

    #############################################@##################################################
    # TODO connect signal/slots to update filters more efficinetly
    #############################################@##################################################

    def _update_filters(self, first, last):
        """
        Update the internal filters definitions based on the removed indexes.
        """

        raise NotImplementedError(
            "TODO optimize by only updating the internal filters def by the udpated indexes"
        )

    def _remove_filters(self, parent, first, last):
        """
        Update the internal filters definitions based on the removed indexes.
        """

        raise NotImplementedError(
            "TODO optimize by only updating the internal filters def by the udpated indexes"
        )

    def _insert_filters(self, parent, first, last):
        """
        Update the internal filters definitions based on the updated indexes.
        """

        raise NotImplementedError(
            "TODO optimize by only updating the internal filters def by the udpated indexes"
        )


class ShotgunFilterMenu(FilterMenu):
    """
    Subclass of FilterMenu for models that inherit the ShotgunModel class. It is not necessary to use
    this menu class, but it is a convenience class to set up the filter menu specificaly for data using
    the ShotgunModel class.
    """

    def __init__(self, parent=None):
        """
        Constructor.

        Set the filter_roles to the ShotgunModel role pointing to its SG data.
        """

        super(ShotgunFilterMenu, self).__init__(parent)

        # Use the SG_DATA_ROLE to extract the data from the ShotgunModel.
        self.set_filter_roles([ShotgunModel.SG_DATA_ROLE])

    def set_filter_model(self, filter_model, connect_signals=True):
        """
        Override the base implementation.

        Ensure the filter_model is a subclass of the ShotgunModel class. Update the menu when the
        model emits its data_refreshed signal.

        :param filter_model: The ShotgunModelthat is used to build the menu filters.
        :type filter_model: :class:`sgtk.platform.qt.QSortFilterProxyModel`
        :param connect_signals: Whether or not to connect model signals to
                                the appropriate filter menu methods; e.g. model
                                layoutChanged and data_refreshed signals will rebuild the menu.
        :type connect_signals: bool
        """

        assert isinstance(filter_model.sourceModel(), ShotgunModel)

        if self._source_model is not None:
            try:
                self._source_model.data_refreshed.disconnect(self.data_refreshed)
            except RuntimeError:
                # Signals were never connected.
                pass

        super(ShotgunFilterMenu, self).set_filter_model(filter_model, connect_signals)

        if connect_signals and self._source_model is not None:
            self._source_model.data_refreshed.connect(self.data_refreshed)

    def data_refreshed(self):
        """
        Slot triggered on SG model `data_refreshed` signal. Force a menu refresh.
        """

        self.refresh(force=True)
