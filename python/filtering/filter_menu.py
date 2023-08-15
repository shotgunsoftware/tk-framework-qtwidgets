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
ShotgunMenu = shotgun_menus.ShotgunMenu

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_model"
)
ShotgunModel = shotgun_model.ShotgunModel


class NoCloseOnActionTriggerShotgunMenu(ShotgunMenu):
    """ShotgunMenu subclass that prevents the menu from closing when an action is triggered."""

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
    # Signal emitted when menu is about to do a complete refresh (e.g. call refresh method)
    menu_about_to_be_refreshed = QtCore.Signal()
    # Signal emitted when menu is finished a complete refreshing (e.g. exit refresh method)
    menu_refreshed = QtCore.Signal()

    def __init__(self, parent=None, refresh_on_show=True):
        """
        Constructor

        :param parent: The parent widget.
        :type parent: :class:`sgtk.platform.qt.QtWidget`
        :param refresh_on_show: True will ensure the menu is up to date on show by always
            refreshing the filters before showing. This will slow performance on menu open,
            but ensures the data is the most up to date. To only refresh the menu on show
            on demand, set the `refresh_on_show` property instead of this parm on init.
        :type refresh_on_show: bool
        """

        super(FilterMenu, self).__init__(parent)

        # The filters definitions that are built based on the current model data, and which are used
        # to build the filter menu UI.
        self._filters_def = FilterMenuFiltersDefinition(self)

        # Set the project id for the filters definition to allow handling SG data.
        bundle = sgtk.platform.current_bundle()
        if bundle.tank.pipeline_configuration.is_site_configuration():
            self._filters_def.default_sg_project_id = None
        else:
            self._filters_def.default_sg_project_id = (
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

        # Flag indicating that the menu is restoring its filter state. This is used to avoid
        # menu refreshes for each filter state retored, and instead having a single refresh at
        # the end.
        self._block_signals = False

        # This is the state of the menu that is waiting to be restored. An app may attempt to
        # restore the filter menu state, but it may not be ready to be restored. Store the
        # state to restore until the menu is ready to do so.
        self._restore_state = {}

        # Flag indicating if the menu should ALWAYS refresh right before it is shown. This
        # will ensure the menu is the most up to date with the current data; however it will
        # take longer for the menu to pop open.
        self.__always_refresh_on_show = refresh_on_show
        # Flag indicating if the menu should refresh on NEXT time it is shown. This flag will
        # be toggled off after the next time it is shown.
        self.__refresh_on_show = False

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

    @property
    def refresh_on_show(self):
        """Get or set the property to refresh menu before showing."""
        return self.__refresh_on_show

    @refresh_on_show.setter
    def refresh_on_show(self, refresh):
        self.__refresh_on_show = refresh

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

    def has_role(self, roles, check_existence=True):
        """
        Check if the filter menu is built using the model item data roles.

        :param check_existence: True will return a bool indicating if at least one of the
            roles is in the filter menu's filter roles, else False. False will return the
            list of roles that are in the filter menu's filter roles.
        :type check_existence: bool

        :return: If check_existence, then True is returned if any of the roles given are
            used by the filter menu, else False. If check_existence is False, then from the
            list of the given roles, only the roles that are used in the filter menu will be
            returned.
        :rtype: bool | List[int]
        """

        result = []

        for role in roles:
            for filter_role in self._filters_def.filter_roles:
                if role == filter_role:
                    if check_existence:
                        return True
                    result.append(role)

        return False if check_existence else result

    def save_state(self):
        """
        Save the current menu filter state.

        :return: The current menu filter state that can be used to restore the menu state at a
            later time.
        :rtype: dict
        """

        state = {}

        for field_id, visible in self._field_visibility.items():
            if not visible or field_id not in self._filters_def._definition:
                # Do not attempt to restore hidden fields.
                continue

            state.setdefault(field_id, {})
            filter_items = self._get_filter_group_items(field_id)
            for filter_item in filter_items:
                action = self._get_filter_group_action(field_id, filter_item.id)
                widget = action.defaultWidget()
                if widget.has_value():
                    filter_data = self._filters_def.get_filter_data(
                        field_id, filter_item.id
                    )
                    if filter_data is None:
                        # Search text filter
                        filter_data = widget.value
                    else:
                        filter_data["default_value"] = widget.value

                        # Remove the icon since a QtGui.QIcon may not be able to be stored in
                        # QSettings. The icon can be recreated from the icon_path field.
                        if "icon" in filter_data:
                            del filter_data["icon"]

                    state[field_id][filter_item.id] = filter_data

        if self._restore_state:
            # Part of the menu state was never restored, merge it with the current state to save.
            for field_id, filter_items in self._restore_state.items():
                if field_id not in state:
                    state[field_id] = filter_items
                else:
                    for item_id, item_data in filter_items.items():
                        state[field_id][item_id] = item_data

        return state

    def restore_state(self, state):
        """
        Restore the menu with the given state.

        If the menu has not been built yet, the state will be restored on first build.

        :param state: The menu state to restore.
        :type state: dict
        """

        if self._filters_def.is_empty():
            # State will be restored when the menu is first built.
            self._restore_state = state
            return

        self._restore_state = self._restore_filter_definition(state)
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
        assert hasattr(
            filter_model, "set_filter_items"
        ), "Filter model must have attribute `set_filter_items`"

        if self._proxy_model:
            try:
                self._proxy_model.modelAboutToBeReset.disconnect(
                    self.menu_about_to_be_refreshed
                )
                self._proxy_model.layoutChanged.disconnect(self.update_filters)
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
            self._proxy_model.modelAboutToBeReset.connect(
                self.menu_about_to_be_refreshed
            )
            self._proxy_model.layoutChanged.connect(self.update_filters)

    @sgtk.LogManager.log_timing
    def refresh(self, force=False):
        """
        Refresh the filter menu.

        This operation will rebuild the underlying filter definition that the filter menu is
        built from. The filter definition is built based on the current filter model data.

        The filter menu widgets will be cleared and rebuilt. The current menu state will be
        saved before rebuild, and restored once the refresh operation is complete.

        Emits `menu_refreshed` signal once refresh is done.
        """

        if self._is_refreshing and not force:
            return

        # Start the menu refresh.
        self._is_refreshing = True

        try:
            # Save the menu state before rebuilding it. It will be restored when the refresh
            # has completed.
            state = self.save_state()
            self.clear_menu()

            # First build only the filter groupings. Individual filters will only be built
            # once it is known they are visible, as it will be a wasted effor to build any
            # filters that are hidden.
            self._filters_def.build(groups_only=True)

            # Restore the menu state before the refresh started. This will show any filters
            # that need to be restored.
            self._restore_state = self._restore_filter_definition(state)

            # Now update the individual filters that are known to be visible.
            field_ids = [
                field_id
                for field_id, visible in self._field_visibility.items()
                if visible
            ]
            self._filters_def.update_filters(field_ids)

            # Create the filter menu actions and widgets based on the filter definition.
            self._build_menu_widgets()

            # After menu has been rebuilt, emit signal that filters have changed to apply the
            # current filtering from the menu.
            self._emit_filters_changed()
        finally:
            self._is_refreshing = False
            self.menu_refreshed.emit()

    def update_filters(self, filter_group_ids=None):
        """Update only the active/visible filters in the menu."""

        if self._block_signals:
            return

        # Refresh the counts of the visible filters.
        if filter_group_ids:
            fields_to_refresh = filter_group_ids
        else:
            filter_group_ids = [
                field_id
                for field_id, visible in self._field_visibility.items()
                if visible
            ]
            fields_to_refresh = None

        self._filters_def.update_filters(filter_group_ids)
        self._refresh_menu_widgets(field_ids=fields_to_refresh)

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

    def clear_filters(self, filter_group_ids=None):
        """Clear any active filtesr that are set in the menu."""

        if not self._filter_groups:
            # No filters to clear.
            return

        # Do not trigger any signals while clearing the filters.
        restore_state = self.blockSignals(True)
        # Set our manual block signals flag since the Qt method to block does not work when
        # we mnaully trigger signals (e.g. call setChecked on a checkbox)
        restore_block_signals_state = self._block_signals
        self._block_signals = True

        # Only emit a change if the menu actually had active filters.
        had_value = False

        # Get the filter groups to clear
        if filter_group_ids:
            filter_groups = []
            num_groups = len(filter_group_ids)
            for group_id, filter_group in self._filter_groups.items():
                if group_id in filter_group_ids:
                    filter_groups.append(filter_group)
                if len(filter_groups) == num_groups:
                    # Found all groups, exit early
                    break
        else:
            # Not specified, clear all.
            filter_groups = self._filter_groups.values()

        try:
            for filter_group in filter_groups:
                for action in filter_group.filter_actions.values():
                    filter_item_widget = action.defaultWidget()
                    if action.isChecked() or filter_item_widget.has_value():
                        had_value = True
                    # Uncheck the QAction.
                    action.setChecked(False)
                    # Clear the value from the FilterItemWidget.
                    filter_item_widget.clear_value()

                if filter_group.search_filter_action:
                    search_filter_widget = (
                        filter_group.search_filter_action.defaultWidget()
                    )
                    if search_filter_widget.has_value():
                        had_value = True
                    search_filter_widget.clear_value()
        finally:
            # Ensure the signals are unblocked.
            self.blockSignals(restore_state)
            self._block_signals = restore_block_signals_state

        if had_value:
            # Clear the active filter and emit the changed signal.
            self._active_filter.filters = []
            if not self._is_refreshing:
                self._emit_filters_changed()

    def get_current_filters(self, exclude_choices_from_fields=None):
        """
        Get the current filters that are active in the menu.

        The menu filtering is built by:
            1. Within a filter field:
                a. All choice filters are grouped with OR, to create a group filter item
                b. The choices filter item is then grouped with the search filter with AND
            2. All filter field group items are then combined with AND to get the final filter item

        If the `exclude_choices_from_fields` is provided, this will not add any choice filters
        from the listed fields. Note that the search filter for these fields will still be
        included. This is used by the filter definition to get filter choice value counts.

        :param exclude_choices_from_fields: The list of fields to exclude when collecting the
            currently active filtering from the menu.
        :type exclude_choices_from_fields: List[str]

        :return: A filter item representing the current filtering in the menu.
        :rtype: List[FilterItem]
        """

        exclude_choices_from_fields = exclude_choices_from_fields or []
        current_filters = []

        for field_id, filter_group in self._filter_groups.items():
            if field_id in exclude_choices_from_fields:
                choices_filters = None
            else:
                # Get the filter items that are active (e.g. have a value set).
                choices_filters = [
                    filter_item
                    for filter_item in filter_group.filter_items
                    if self._get_filter_group_action(field_id, filter_item.id)
                    .defaultWidget()
                    .has_value()
                ]

            search_filter_item = None
            if filter_group.search_filter_action and filter_group.search_filter_item:
                if filter_group.search_filter_action.defaultWidget().has_value():
                    search_filter_item = filter_group.search_filter_item

            if choices_filters and search_filter_item:
                # Add a filter OR all choice filtesr together, within the field, and AND it
                # with the search filter.
                choices_filter_group = FilterItem.create_group(
                    FilterItem.FilterOp.OR,
                    group_filters=choices_filters,
                    group_id=field_id,
                )
                current_filters.append(
                    FilterItem.create_group(
                        FilterItem.FilterOp.AND,
                        group_filters=[choices_filter_group, search_filter_item],
                        group_id=field_id,
                    )
                )
            elif choices_filters:
                # Add just the filter OR all choice filtesr together, within the field
                current_filters.append(
                    FilterItem.create_group(
                        FilterItem.FilterOp.OR,
                        group_filters=choices_filters,
                        group_id=field_id,
                    )
                )
            elif search_filter_item:
                # Add just the search filter.
                current_filters.append(search_filter_item)

        return current_filters

    def initialize_menu(self):
        """
        Initialize the filter menu.

        This method no longer needs to be called to initialize the menu since refresh will
        take care of re-initializing. This method now just calls refresh for backward
        compatibility.
        """

        self.refresh()

    #############################################@##################################################
    # Protected methods
    #############################################@##################################################

    @sgtk.LogManager.log_timing
    def _build_menu_widgets(self):
        """Initialize the menu by building the menu action and widgets."""

        # Add the static menu actions
        clear_action = self.addAction("Clear All Filters")
        clear_action.triggered.connect(self.clear_filters)

        # Build and add the configuration menu as a submenu to the main filter menu.
        self._more_filters_menu = NoCloseOnActionTriggerShotgunMenu(self)
        self._more_filters_menu.setTitle("More Filters")
        self.addMenu(self._more_filters_menu)

        self.addSeparator()

        # Build the filter menu actions and their widgets from the filter definition.
        sorted_field_ids = self._filters_def.get_fields(sort=True)
        self._add_filter_groups(sorted_field_ids)

    @sgtk.LogManager.log_timing
    def _refresh_menu_widgets(self, field_ids=None):
        """
        Update the menu actions and widgets based on the current filter definition.

        Iterate through the filter items by field group:
            - Filter item field groups will be removed as a whole, if the current FilterDefinition
              does have a record of the field.
            - Individual filter items will be removed, if the FilterDefinition no longer has a
              record of it.
            - Filter item counts will be updated according to the current FilterDefinition
            - Individual filter items will be added, if the field it belongs to already exists

        :param field_ids: The menu group fields to update.
        :type field_ids: List[str]
        """

        restore_block_signals_state = self._block_signals
        self._block_signals = True
        try:
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
                updated_filters_values = data.get("values", {})
                # Update existing filter item widget counts
                existing_value_ids = []
                # Copy the filter items since we may be removing some items as we go.
                current_filter_items = list(filter_group.filter_items)
                for item in current_filter_items:
                    action = self._get_filter_group_action(field_id, item.id)
                    if not isinstance(action.defaultWidget(), ChoicesFilterItemWidget):
                        # Only ChoicesFilterItemWidgets need updating
                        continue

                    existing_value_ids.append(item.id)
                    filter_value = updated_filters_values.get(item.id)
                    if filter_value is not None and (
                        action.defaultWidget().has_value()
                        or filter_value.get("count", 0) > 0
                    ):
                        # Update the widget count label
                        action.defaultWidget().set_value(filter_value)
                    else:
                        # Filter item no longer has any values, remove it
                        self._remove_filter_action(field_id, item)

                # Insert any new filter items into an existing group.
                for value_id, value_data in updated_filters_values.items():
                    if value_id in existing_value_ids:
                        continue

                    filter_item, filter_action = self._create_filter_item_and_action(
                        field_id, data, value_id, value_data
                    )
                    filter_group.insert_into_menu(self, filter_item, filter_action)

            # The menu layout may have changd, ensure it is positioned nicely.
            self._adjust_position()
        finally:
            self._block_signals = restore_block_signals_state

    def _restore_filter_definition(self, state):
        """
        Restore the filter definition from the current menu state to restore.

        :param state: The filter menu state to restore.
        :type state: dict

        :return: If any of the state  was not restored, this will be returned.
        :rtype: dict
        """

        # Keep track of what filters were not restored so that they may be restored at a later
        # time when possible.
        not_restored = {}

        for field_id, filter_items in state.items():
            if field_id not in self._filters_def._definition:
                not_restored[field_id] = filter_items
                continue

            # Ensure the group the filter is in is visible.
            self._field_visibility[field_id] = True
            items_not_restored = {}
            for value_id, filter_data in filter_items.items():
                # Check if the current filter definition set has the choice filter available.
                # Note, this will always return false for search text filters
                if self._filters_def.has_filter(field_id, value_id):
                    if isinstance(filter_data, dict):
                        # Ensure the icon is created, since it was removed on save.
                        if filter_data.get("icon_path") and not filter_data.get("icon"):
                            filter_data["icon"] = QtGui.QIcon(filter_data["icon_path"])
                        self._filters_def.set_filter_data(
                            field_id, value_id, filter_data
                        )
                    else:
                        self._filters_def.set_default_value(
                            field_id, value_id, filter_data
                        )
                else:
                    if isinstance(filter_data, dict):
                        # Choices filter that cannot be restored with the available filters,
                        # save it to be restored at a later time.
                        items_not_restored[value_id] = filter_data
                    else:
                        # Restore the search text filter
                        self._filters_def.set_default_value(
                            field_id, value_id=None, default_value=filter_data
                        )

            if items_not_restored:
                not_restored[field_id] = items_not_restored

        return not_restored

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
            if not field_data:
                # There is no filter definition for this field.
                continue

            filter_item_and_actions = []
            if field_data["type"] == FilterItem.FilterType.STR:
                # Create a text search filter item.
                filter_id = self._get_search_filter_item_id(field_id)
                search_filter_item_and_action = self._create_filter_item_and_action(
                    field_id, field_data, filter_id
                )
            else:
                search_filter_item_and_action = None

            # Create filter items for list of value choices
            filter_values = field_data.get("values", {})
            # NOTE this could be optimized by only creating the filter choice values that are
            # shown (the grouping shows only up to a maximum number), and then creating the
            # items on showing more
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
            filter_group.add_to_menu(
                self,
                filter_item_and_actions,
                field_data["name"],
                search_filter_item_and_action=search_filter_item_and_action,
            )

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
            display_name = filter_value.get("name", str(filter_id))
            filter_item_data.update(
                {
                    "filter_type": field_data["type"],
                    "filter_op": FilterItem.default_op_for_type(field_data["type"]),
                    "filter_value": filter_value.get("value"),
                    "display_name": display_name,
                    "short_name": filter_value.get("short_name", display_name),
                    "count": filter_value.get("count", 0),
                    "icon_path": filter_value.get("icon_path"),
                    "icon": filter_value.get("icon"),
                    "default_value": filter_value.get("default_value"),
                }
            )
        else:
            filter_widget_class = TextFilterItemWidget
            filter_item_data["filter_type"] = FilterItem.FilterType.STR
            filter_item_data["filter_op"] = FilterItem.FilterOp.IN
            filter_item_data["display_name"] = field_data.get("name")
            filter_item_data["short_name"] = field_data.get("short_name")
            # The default value is in the field data since it is applicable to the whole
            # filter group.
            filter_item_data["default_value"] = field_data.get("default_value")

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
        widget_action.setCheckable(True)

        widget = widget_class(filter_item.id, field_id, filter_data)
        widget_action.setDefaultWidget(widget)
        if filter_data.get("default_value") is not None:
            widget.value = filter_data["default_value"]
            # Ensure the filter item value is updated to the default value.
            if filter_item.filter_value is None:
                filter_item.filter_value = filter_data["default_value"]

        # Connect action and widget signal/slots after they are initialized (to avoid
        # triggering any signals on creation).
        widget.state_changed.connect(
            lambda state, a=widget_action: self._filter_widget_checked(a, state)
        )
        widget.value_changed.connect(
            lambda text, f=filter_item: self._filter_widget_value_changed(f, text)
        )

        if isinstance(widget, ChoicesFilterItemWidget):
            # Only connect signal/slot to update value based on check state, if the filter
            # item is checkable (e.g. do not connect this for TextFilterItemWidgets).
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

    def _remove_filter_action(self, field_id, filter_item, force=False):
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
            if isinstance(action.defaultWidget(), ChoicesFilterItemWidget):
                # Reset count to 0 for choices filter widgets
                action.defaultWidget().set_value({"count": 0})

            if not force:
                # Do not remove a filter if it has a value
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

        # Connect this signal/slot after setting the filter widget value to avoid triggering it.
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
        """Update the active filter and emit a signal that the filters have changed."""

        if self._block_signals:
            return

        self._active_filter.filters = self.get_current_filters()
        self._update_model_filters()
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
        return "{}.{}".format(field_id, str(TextFilterItemWidget))

    def _get_filter_group_items(self, field_id):
        """
        Convenience method to get all filter items for a given group.

        :param field_id: The field group to get the items from.
        :type field_id: str

        :return: The filter group's items
        :rtype: list<FilterItem>
        """

        filter_group = self._filter_groups.get(field_id)
        if not filter_group:
            return []

        filter_items = self._filter_groups[field_id].filter_items

        if filter_group.search_filter_item:
            filter_items.append(filter_group.search_filter_item)

        return filter_items

    def _get_filter_group_action(self, field_id, filter_id):
        """
        Convenience method to get an action from a filter group.

        :param field_id: The field group to get the action from.
        :type field_id: str

        :return: The filter group's action.
        :rtype: QAction
        """

        filter_group = self._filter_groups.get(field_id)
        if not filter_group:
            return None

        if (
            filter_group.search_filter_item
            and filter_group.search_filter_item.id == filter_id
        ):
            return filter_group.search_filter_action

        return filter_group.filter_actions.get(filter_id)

    def _adjust_position(self):
        """Adjust the menu to ensure all actions are visible."""

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
        """Callback triggered when the menu is about to show."""

        # Ensure the menu is up to date on show.
        if self.__always_refresh_on_show or self.refresh_on_show:
            self.refresh()
            self.refresh_on_show = False

    def _update_model_filters(self):
        """Update the filter model to reflect the current filtering set based on the menu."""

        if not self._proxy_model:
            return

        self._proxy_model.set_filter_items([self.active_filter])

    def _toggle_filter_group(self, action, state):
        """
        Callback triggered when a filter widget action state has changed.

        If the filter widget has been checked, then ensure its filter group is visible.

        :param action: The filter widget action.
        :type action: QtGui.QWidgetAction
        :param state: The filter widget action state.
        :type state: QtCore.Qt.CheckState
        """

        action.setChecked(state == QtCore.Qt.Checked)
        widget = action.defaultWidget()
        checked = widget.has_value()
        field_id = widget.group_id

        # Keep track of the field group visibility.
        self._field_visibility[field_id] = checked
        self._filter_groups[field_id].set_visible(checked)

        # Ensure the filter value counts are up to date on show.
        self.update_filters(filter_group_ids=[field_id])

        self._adjust_position()

    def _filter_widget_checked(self, action, state):
        """
        Callback triggered when a FilterItemWidget `state_changed` signal emitted.

        :param action: The menu action associated with the filter widget.
        :type action: :class:`sgtk.platform.qt.QtGui.QAction`
        :param state: The filter widget's checkbox state.True
        :type state: :class:`sgtk.platform.qt.QtCore.Qt.CheckState`
        """

        # Keep the parent QAction checked state in sync with the filter item widget's checkbox state.
        checked = state == QtCore.Qt.Checked
        action.setChecked(checked)
        self._emit_filters_changed()

    def _filter_widget_value_changed(self, filter_item, text):
        """
        Callback triggered when a FilterItemWidget `value_changed` signal emitted.

        :param filter_item: The FilterItem assoicated with the filter widget.
        :type filter_item: FilterItem
        :param text: The new text value the filter widget has.
        :type text: str
        """

        updated = filter_item.set_filter_value(text)
        if updated:
            self._emit_filters_changed()


class ShotgunFilterMenu(FilterMenu):
    """
    Subclass of FilterMenu for models that inherit the ShotgunModel class. It is not necessary to use
    this menu class, but it is a convenience class to set up the filter menu specificaly for data using
    the ShotgunModel class.
    """

    def __init__(self, parent=None, refresh_on_show=True):
        """
        Constructor.

        Set the filter_roles to the ShotgunModel role pointing to its SG data.
        """

        super(ShotgunFilterMenu, self).__init__(parent, refresh_on_show=refresh_on_show)

        # Use the SG_DATA_ROLE to extract the data from the ShotgunModel. This class fixes the
        # filte roles to the ShotgunModel.SG_DATA_ROLE since it is designed to work with this
        # model only.
        self._filters_def.filter_roles = [ShotgunModel.SG_DATA_ROLE]
        self.__field_id_prefix = str(ShotgunModel.SG_DATA_ROLE)

    def set_filter_roles(self, roles):
        """Override the base method to not allow manually setting the roles."""

        # Do nothing. The filter roles are fixed. Use the FilterMenu class if the filter roles
        # need to be modified.

    def set_visible_fields(self, fields):
        """
        Override the base method to ensure field ids are prefixed with the role.

        Set the filters that belong to any of the given fields to be visible.

        :param fields: The filters within the given fields will be shown.
        :type fields: list<str>
        """

        if not fields:
            return

        for field in fields:
            if not field.startswith(self.__field_id_prefix):
                field = "{}.{}".format(self.__field_id_prefix, field)
            self._field_visibility[field] = True

    def set_accept_fields(self, fields):
        """
        Override the base method to ensure field ids are prefixed with the role.

        Set the fields to ignore when building the filter definition for the menu.

        :param fields: The fields to ignore
        :type fields: list<str>
        """

        # Ensure field ids have the correct field id prefix.
        for i, field in enumerate(fields):
            if not field.startswith(self.__field_id_prefix):
                field = "{}.{}".format(self.__field_id_prefix, field)
                fields[i] = field

        self._filters_def.accept_fields = fields

    def set_ignore_fields(self, fields):
        """
        Override the base method to ensure field ids are prefixed with the role.

        Set the fields to ignore when building the filter definition for the menu.

        :param fields: The fields to ignore
        :type fields: list<str>
        """

        # Ensure field ids have the correct field id prefix.
        for i, field in enumerate(fields):
            if not field.startswith(self.__field_id_prefix):
                field = "{}.{}".format(self.__field_id_prefix, field)
                fields[i] = field

        self._filters_def.ignore_fields = fields

    def restore_state(self, state):
        """Override the base method to ensure field ids are prefixed with the role."""

        formatted_state = {}
        for field_id, field_state in state.items():
            if not field_id.startswith(self.__field_id_prefix):
                field_id = "{}.{}".format(self.__field_id_prefix, field_id)
            formatted_state[field_id] = field_state

        super(ShotgunFilterMenu, self).restore_state(formatted_state)

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
                self._source_model.data_refreshing.disconnect(self._on_data_refreshing)
                self._source_model.data_refresh_fail.disconnect(
                    self._on_data_refresh_fail
                )
                self._source_model.data_refreshed.disconnect(self._on_data_refreshed)
                self._source_model.cache_loaded.disconnect(self._on_cache_loaded)
            except RuntimeError:
                # Signals were never connected.
                pass

        super(ShotgunFilterMenu, self).set_filter_model(filter_model, connect_signals)

        if connect_signals and self._source_model is not None:
            self._source_model.data_refreshing.connect(self._on_data_refreshing)
            self._source_model.data_refresh_fail.connect(self._on_data_refresh_fail)
            self._source_model.data_refreshed.connect(self._on_data_refreshed)
            self._source_model.cache_loaded.connect(self._on_cache_loaded)

    def _on_data_refreshing(self):
        """
        Slot triggered on SG model `data_refreshing` signal.

        Emit the signal that the menu is about to refresh now.
        """

        self.menu_about_to_be_refreshed.emit()

    def _on_data_refresh_fail(self, msg):
        """
        Slot triggered on SG model `data_refresh_fail` signal.

        Refresh failed will not trigger the menu refresh, but we still need to emit the signal
        menu finished refreshing since the menu_about_to_be_refreshed signal has been emitted.
        """

        self.menu_refreshed.emit()

    def _on_data_refreshed(self):
        """
        Slot triggered on SG model `data_refreshed` signal.

        Force a menu refresh.
        """

        self.refresh(force=True)

    def _on_cache_loaded(self):
        """
        Slot triggered on SG model `cache_loaded` signal.

        Force a menu refresh.
        """

        self.refresh(force=True)
