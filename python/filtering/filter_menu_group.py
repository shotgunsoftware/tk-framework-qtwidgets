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


shotgun_menus = sgtk.platform.current_bundle().import_module("shotgun_menus")
ShotgunMenu = shotgun_menus.ShotgunMenu

sg_qicons = sgtk.platform.current_bundle().import_module("sg_qicons")
SGQIcon = sg_qicons.SGQIcon

sg_qwidgets = sgtk.platform.current_bundle().import_module("sg_qwidgets")
SGQWidget = sg_qwidgets.SGQWidget
SGQToolButton = sg_qwidgets.SGQToolButton


class FilterMenuGroup(object):
    """Class object to manage a filter grouping within a QMenu."""

    def __init__(self, group_id, show_limit=5, show_limit_increment=None):
        """
        Constructor. Initialize the filter group's instance members.
        """

        # The unique identifier for this filter group.
        self.group_id = group_id

        # The limit to how many items are shown in the group.
        self._show_limit = show_limit
        # The incremental amount to the limited number of items shown in the group; e.g.
        # the group may have a limit to show only 5 items, if the user requets to increase
        # the number of items shown, this is the amount that the limit will increase by.
        self._show_limit_increment = show_limit_increment or show_limit

        # The header QWidgetAction for this group.
        self.header_action = None
        # The show/hide action to toggle the filter group visibility.
        self.show_hide_action = None
        # The list of FilterItem objects that belong to this group.
        self.filter_items = []
        # The mapping of FilterItem id to its corresponding QWidgetAction.
        self.filter_actions = {}

        self._search_filter_item = None
        self._search_filter_action = None

        # A reserve list of actions, which are hidden, but ready to be shown on user request.
        # There is a limit to how many items are shown at a given time to avoid having an
        # overwhelming amount of items in a menu). These items will incrementally show when
        # the "Show More..." action is triggered.
        self.more_actions = []
        # This action will trigger showing more items in the group incrementall. It will always
        # be shown as the last item in the group.
        self.show_more_action = QtGui.QAction("Show More...", None)
        self.show_more_action.triggered.connect(self.show_more)

    @staticmethod
    def set_action_visible(action, visible):
        """
        Convenience method to set the action visible. If the action is a QWidgetAction and has a
        widget, its widget willalso be set visible or not.

        :param action: The action to set its visibility.
        :type action: :class:`sgtk.platform.qt.QAction`
        :param visible: Whether or not the action is visible.
        :type visible: bool
        """

        if action.isVisible() != visible:
            action.setVisible(visible)
            try:
                widget = action.defaultWidget()
                widget.setVisible(visible)

                # Attempt to clear the widget's filter value, if the default widget has the required
                # methods defined.
                if not visible and widget.has_value():
                    widget.clear_value()

            except AttributeError:
                # This is a QAction which does not have a `defaultAction`, or is a QWidgetAction
                # without a default widget, or a QWidgetAction with a default wigdet without
                # attributes `has_value` and `clear_value`.
                pass

    @staticmethod
    def filter_action_widget_has_value(filter_action):
        """
        Return True if the filter action has a value currently set.

        This expects the filter action to be a QWidgetAction with a default widget that implements
        the method `has_value` (e.g. FilterItemWidget class object), otherwise False is returned.

        :param filter_action: The filter action to check if has value.
        :type filter_action: QWidgetAction

        :return: True if the filter action has a value set, else False.
        :rtype: bool
        """

        try:
            return filter_action.defaultWidget().has_value()
        except AttributeError:
            return False

    @staticmethod
    def get_sort_value(action):
        """
        Return the value used to sort the filter group actions.
        """

        try:
            # For QWidgetAction objects, try to extract the name of its default widget.
            # NOTE the default widget is a plain QWidget, so the default widget must
            # subclass QWidget and define a `name` method (see FilterItemWidget).
            sort_value = action.defaultWidget().name
        except AttributeError:
            # Default to sorting by the QAction's display value.
            sort_value = action.text()

        return sort_value.lower()

    @staticmethod
    def get_primary_sort(action):
        """ """

        return 0 if action.isChecked() else 1

    @property
    def search_filter_item(self):
        """Get the search text filter item for this group."""
        return self._search_filter_item

    @property
    def search_filter_action(self):
        """Get the search text filter action for this group."""
        return self._search_filter_action

    #############################################@##################################################
    # Public methods
    #############################################@##################################################

    def get_sorted_actions(self):
        """Return the filter actions in sorted order according to the action display values."""

        return sorted(self.filter_actions.values(), key=self.get_sort_value)

    def get_next_actions(self, num):
        """
        Return a list of `num` actions that are next in line to be shown. If there are less than
        `num` actions in the reserve list to be shown, the number of actions returned will be
        the number of actions in the reserve list.

        :param num: The next number of actions to get.
        :type num: int

        :return: The list of next actions ready to be shown.
        :rtype: list<:class:`sgtk.platform.qt.QAction`>
        """

        return sorted(self.more_actions, key=self.get_sort_value)[:num]

    def add_item(self, filter_item, filter_action):
        """
        Add the filter item and its corresponding QWidgetAction to the group.

        :param filter_item: The filter item to add.
        :type filter_item: FilterItem
        :param filter_action: The widget action that corresponds to the filter item.
        :type filter_action: :class:`sgtk.platform.qt.QAction`
        """

        self.filter_items.append(filter_item)
        self.filter_actions[filter_item.id] = filter_action

        # After adding an item, need to check if the show limit has been exceeded.
        sorted_actions = self.get_sorted_actions()
        action_index = sorted_actions.index(filter_action)

        if len(sorted_actions) > self._show_limit:
            # The limit has been exceeded, need to move an action to the reserve list.
            if action_index < self._show_limit:
                # Another action got bumped, hide that one.
                hide_action = sorted_actions[self._show_limit]
                hide_action_index = self._show_limit
            else:
                # The action being added is not initially visible.
                hide_action = filter_action
                hide_action_index = action_index

            if self.filter_action_widget_has_value(hide_action):
                # Do not hide actions that have a value set. Instead increase the show limit.
                self._increase_show_limit(
                    action_index=hide_action_index, sorted_actions=sorted_actions
                )
            else:
                # Make sure the action is hidden and its filter value is cleared.
                if hide_action not in self.more_actions:
                    self.more_actions.append(hide_action)
                self.set_action_visible(hide_action, False)

        # The "Show More..." action will need to be shown if adding an action has
        # caused exceeding the show limit.
        self._update_show_more_visibility()

    def remove_item(self, filter_item):
        """
        Remove the filter item, and its corresponding QWidgetAction from the group.

        :param filter_item: The filter item to remove from the group.
        :type filter_item: FilterItem
        """

        if self.search_filter_item and filter_item.id == self.search_filter_item.id:
            self._search_filter_action = None
        else:
            try:
                self.filter_items.remove(filter_item)
            except ValueError:
                # Didn't find the filter item, just continue.
                return

            action = self.filter_actions.get(filter_item.id)
            if not action:
                # Didn't find the filter action, exit now.
                return

            del self.filter_actions[filter_item.id]

            if action in self.more_actions:
                # Make sure to take it out of the reserve list and potentially hide the "Show More..."
                # action if this was the only action in the reserve list.
                self.more_actions.remove(action)
                self._update_show_more_visibility()
            else:
                # Check if there is a new action actions to show in place of the item that was removed.
                self.show_more(num=1, increase_limit=False)

    def add_to_menu(
        self,
        menu,
        filter_item_and_actions,
        title=None,
        separator=True,
        search_filter_item_and_action=None,
    ):
        """
        Adds a group of items to the menu.

        :param items: A list of actions and/or menus to add to this menu.
        :type items: list
        :param title: Optional text to use in a label at the top of the group.
        :tupe title: str
        :param separator: Add a separator if True (default), don't add if False.
        :type separator: bool
        """

        if search_filter_item_and_action is None:
            self._search_filter_item = None
            self._search_filter_action = None
        else:
            (
                self._search_filter_item,
                self._search_filter_action,
            ) = search_filter_item_and_action
            # Sanity check
            assert self._search_filter_item, "Missing required search filter item"
            assert self._search_filter_action, "Missing required search filter action"

        if not menu.isEmpty() and separator:
            menu.addSeparator()

        if title:
            # Add the filter group title menu entry (with actions)
            reset_action = QtGui.QAction("Reset Filter")
            reset_action.triggered.connect(
                lambda checked=False, m=menu: self.reset_filters(m)
            )
            remove_action = QtGui.QAction("Remove Filter")
            remove_action.triggered.connect(lambda checked=False: self.remove_filters())
            # Create action menu for filter group
            filter_group_action_menu = ShotgunMenu(menu)
            filter_group_action_menu.setTitle(title)
            filter_group_action_menu.add_group([reset_action, remove_action])
            # Create the action button that will display menu on click
            filter_group_action_menu_button = SGQToolButton(
                menu, icon=SGQIcon.gear(size=SGQIcon.SIZE_16x16)
            )
            filter_group_action_menu_button.setStyleSheet("padding: 2px 4px 2px 4px")
            filter_group_action_menu_button.setCheckable(False)
            filter_group_action_menu_button.setPopupMode(QtGui.QToolButton.InstantPopup)
            filter_group_action_menu_button.setMenu(filter_group_action_menu)
            # Get the formatted label from the ShotgunMenu class
            label = filter_group_action_menu.get_label(title)
            # Create the widget to hold the title and action button
            header_action_widget = SGQWidget(
                menu, child_widgets=[label, None, filter_group_action_menu_button]
            )

            # Create the widget action to display the filter group title and filter group actions
            self.header_action = QtGui.QWidgetAction(menu)
            self.header_action.setDefaultWidget(header_action_widget)
            menu.addAction(self.header_action)

        # First add the search filter (if provided), so it appears on top of all other choice filters.
        if self._search_filter_item and self._search_filter_action:
            menu.addAction(self._search_filter_action)

        # Before adding the items to the menu, check if the show limit needs to be increased
        # in order to.
        sorted_items = sorted(
            filter_item_and_actions, key=lambda item: self.get_sort_value(item[1])
        )
        increase_limit = 0
        for index, (filter_item, action) in enumerate(sorted_items[self._show_limit :]):
            if self.filter_action_widget_has_value(action):
                increase_limit = index + 1
        self._show_limit += increase_limit

        # Now add all choice filters.
        for filter_item, action in sorted_items:
            self.add_item(filter_item, action)

            if isinstance(action, QtGui.QMenu):
                menu.addMenu(action)
            else:
                menu.addAction(action)

        # Always add the "Show More..." action to the ned of the group, it will also help
        # keep track of the last action in the filter group.
        menu.addAction(self.show_more_action)

    def insert_into_menu(self, menu, filter_item, action):
        """
        Insert the action into the menu in the correct order. The order is determined by
        the `get_sorted_actions` method.

        :param menu: The menu to add the action into.
        :type menu: :class:`sgtk.platform.qt.QMenu`
        :param action: The action to add into the menu.
        :type action: :class:`sgtk.platform.qt.QAction`
        """

        self.add_item(filter_item, action)

        insert_before = self._get_insert_before_action(action)
        menu.insertAction(insert_before, action)

        if self.filter_action_widget_has_value(action) and not action.isVisible():
            # The item inserted has a value but is hidden. In that case, we need to extend the
            # show limit and set all action visible that are within the new limit.
            self._increase_show_limit(action=action)

    def show_more(self, num=None, increase_limit=True):
        """
        Show `num` more gorup item actions. If `increase_limit` is True, the group will
        increase the limit of items able to show by the group's increment.

        :param n: The number of actions to show. Defaults to the group's increment.
        :type n: int
        :param increase_limit: True will increase the group's show limimt.
        :type increase_limit: bool
        """

        num = num or self._show_limit_increment

        if increase_limit:
            self._show_limit += self._show_limit_increment
        else:
            # Group limit is not incrasing, so ensure that the limit is being exceeded.
            num_visible = len(
                [a for a in self.filter_actions.values() if a.isVisible()]
            )
            num_available = self._show_limit - num_visible
            num = min(num_available, num)

        actions_to_show = self.get_next_actions(num)
        for action in actions_to_show:
            self.more_actions.remove(action)
            self.set_action_visible(action, True)

        self._update_show_more_visibility()

    def show_action(self, action):
        """
        Show the action. If the action is not in the filter group, nothing is done.

        :param action: The action to show
        :type action: :class:`sgtk.platform.qt.QtGui.QAction`
        """

        if action not in self.filter_actions.values():
            return

        if action in self.more_actions:
            self.more_actions.remove(action)

        self.set_action_visible(action, True)
        self._update_show_more_visibility()

    def set_visible(self, visible):
        """
        Show or hide the widgets within this filter group.

        :param visible: True will show the group widgets, else hides them.
        :type visible: bool
        """

        # Iterate over the actions in sorted order to hide the correct actions if there
        # are more actions than the limit.
        sorted_actions = self.get_sorted_actions()
        for i, action in enumerate(sorted_actions):
            if action in self.more_actions:
                # Skip hidden actions
                continue

            if visible:
                if i < self._show_limit:
                    self.set_action_visible(action, True)
                else:
                    self.more_actions.append(action)
                    self.set_action_visible(action, False)
            else:
                self.set_action_visible(action, False)

        # Set the new visibility for the header action
        if self.header_action:
            self.set_action_visible(self.header_action, visible)

        # Set the new visibility for the search action
        if self.search_filter_action:
            self.set_action_visible(self.search_filter_action, visible)

        if not visible:
            # Reset the show limit
            self._show_limit = self._show_limit_increment
            # Hide the "Show More..." action
            self.set_action_visible(self.show_more_action, False)
        else:
            self._update_show_more_visibility()

    def reset_filters(self, menu):
        """
        Reset the filter group by clearing all filters within the group.

        :param menu: The parent menu this filter group belongs to.
        :type menu: :class:`FilterMenu`
        """

        menu.clear_filters([self.group_id])

    def remove_filters(self):
        """
        Remove the filter group from the menu.

        This will clear any filters that are set in the group before removing the widgets.
        """

        # Get and trigger the menu action that removes the filter group
        w = self.show_hide_action.defaultWidget()
        w.clear_value()

    #############################################@##################################################
    # Protected methods
    #############################################@##################################################

    def _get_insert_before_action(self, action):
        """
        Return the QAction that the `action` should be inserted before. The order is determined
        by the `get_sorted_actions` method.

        :param action: The action to find the action in the group that it should be inserted before.
        :type action: :class:`sgtk.platform.qt.QAction`
        """

        sorted_actions = self.get_sorted_actions()
        action_index = sorted_actions.index(action)

        if action_index + 1 < len(sorted_actions):
            return sorted_actions[action_index + 1]

        # Append the action to the group by inserting before the "Show More..." action (since
        # the "Show More..." action will always be the last item in the group).
        return self.show_more_action

    def _update_show_more_visibility(self):
        """
        Show "Show More..." action if there are actions in the reserve list waiting to be shown, or
        hide it if there are none.
        """

        show_more_visible = bool(self.more_actions)
        self.set_action_visible(self.show_more_action, show_more_visible)

    def _increase_show_limit(self, action=None, action_index=None, sorted_actions=None):
        """
        Increase the menu item show limit to include the given action or action index.

        This will increase the show limit up to the given action or index, and show all items
        up to the new show limit.

        An action or action index must be passed to determine the new show limit. Optionally,
        the menu list of actions (in sorted order) can be passed, if not, `get_sorted_actions`
        will be called.

        :param action: The action whose index will be used to increase the show limit.
        :type action: QWidgetAction
        :param action_index: The index of the action within the menu (sorted) list.
        :type action_index: int
        :param sorted_actions: Optionally pass the menu action item list in sorted order.
        :type sorted_actions: List[QWidgetAction]
        """

        assert action or action_index

        if sorted_actions is None:
            sorted_actions = self.get_sorted_actions()

        if action_index is None:
            action_index = sorted_actions.index(action)

        new_limit = action_index + 1

        for i in range(self._show_limit, new_limit):
            filter_action = sorted_actions[i]
            if filter_action in self.more_actions:
                self.more_actions.remove(filter_action)
            self.set_action_visible(filter_action, True)

        # Update the new show limit
        self._show_limit = new_limit
