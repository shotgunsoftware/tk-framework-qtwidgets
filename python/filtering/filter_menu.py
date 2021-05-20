# Copyright (c) 2021 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.
import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .filter_item import FilterItem
from .filter_item_widget import FilterItemWidget
from ..shotgun_menus import ShotgunMenu

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals"
)


# class FilterMenuButton(QtGui.QToolButton):
#     """
#     TODO finish implementing
#     """

#     def __init__(self, *args, **kwargs):
#         """
#         Constructor
#         """

#         super(FilterMenuButton, self).__init__(*args, **kwargs)

#         self.setPopupMode(QtGui.QToolButton.InstantPopup)
#         self.setText("Filters")
#         # self.setIcon()

#         self._menu = None

#     def setMenu(self, menu):
#         """
#         """

#         super(FilterMenuButton, self).setMenu(menu)

#         if self._menu:
#             self._menu = None
#             # Clean up? disconnect signals, delete later?

#         self._menu = menu
#         self._menu.connect.filters_changed.connect(self._filters_changed)

#     def _filters_changed(self):
#         """
#         Callback on filter menu changes.
#         """

#         self.setChecked(self._menu.has_filtering)


class FilterMenu(ShotgunMenu):
    """"""

    filters_changed = QtCore.Signal()

    def __init__(self, filters, parent, fields=None):
        """
        Constructor
        """

        super(FilterMenu, self).__init__(parent)

        # FIXME Let it be resizable
        # self.setMinimumWidth(250)
        # self.setMaximumWidth(250)

        # TODO add filter -- would need to requery with added fields if data is not available
        # TODO save filter state
        if fields:
            self._visible_fields = fields or []
        else:
            # Take the first three if visible filters is not defined (to avoid overwhelming number of filters)
            self._visible_fields = [f["field"] for f in filters[:3]]

        self._group_filters = []
        # self._config_actions = []
        self._config_menu = ShotgunMenu(self)
        self._config_menu.setTitle("More Filters")

        self.build_menu(filters)

    def build_menu(self, filters_list):
        """
        """

        self.clear_menu()

        # self._config_menu = ShotgunMenu(self)
        # self._config_menu.setTitle("More Filters")

        for filter_group in filters_list:
            actions = []
            filters = []

            filter_defs = filter_group.get("filters", [])
            if not filter_defs:
                # FIXME handle filter widgets based on type better than this - this now needs to be insync with FilterItemWidget create method
                if filter_group.get("filter_type") in (
                    FilterItem.TYPE_NUMBER,
                    FilterItem.TYPE_STR,
                    FilterItem.TYPE_TEXT,
                ):
                    filter_data = {
                        "filter_type": filter_group.get("filter_type"),
                        "filter_op": filter_group.get("filter_op"),
                        "data_func": filter_group.get("data_func"),
                    }
                    (filter_item, action) = self.create_filter_item_and_action(
                        filter_data
                    )
                    filters.append((filter_item, action))
                    actions.append(action)

                else:
                    for filter_name, filter_value in filter_group.get(
                        "filter_value", {}
                    ).items():
                        filter_data = {
                            "filter_type": filter_group.get("filter_type"),
                            "filter_op": filter_group.get("filter_op"),
                            "data_func": filter_group.get("data_func"),
                            "filter_value": filter_value.get("value"),
                            "display_name": filter_value.get("name", str(filter_name)),
                            "count": filter_value.get("count", 0),
                        }
                        (filter_item, action) = self.create_filter_item_and_action(
                            filter_data
                        )
                        filters.append((filter_item, action))
                        actions.append(action)

            self._group_filters.append(filters)

            sorted_actions = sorted(actions, key=lambda item: item.text())
            group_actions = self.add_group(sorted_actions, filter_group.get("name"))

            # TODO custom widget to avoid closing the menu on selecting the checkbox options
            config_action = self._config_menu.addAction(filter_group.get("name"))
            # self._config_actions.append(config_action)
            config_action.setCheckable(True)
            # FIXME this shows nothing if not sg fields
            config_action.setChecked(
                not self._visible_fields
                or filter_group.get("field") in self._visible_fields
            )
            # Should we not even add it in the first place if its not visible?
            self.toggle_action_group(config_action, group_actions)
            # config_action.triggered.connect(lambda actions=group_actions: self.toggle_action_group(actions))
            config_action.triggered.connect(self.toggle_action_group_cb)
            # self._group_actions_by_field[filter_group.get("name")] = group_actions
            for a in group_actions:
                a.setProperty("id", filter_group.get("name"))

        if self.actions():
            self.addSeparator()
            clear_action = self.addAction("Clear All Filters")
            clear_action.triggered.connect(self.clear_filters)

            self.addMenu(self._config_menu)

        # Defaults to no filters active after rebuild
        self._active_filter = FilterItem(
            FilterItem.TYPE_GROUP, FilterItem.OP_AND, filters=[]
        )

    def clear_menu(self):
        """
        """

        # for a in self._config_actions:
        # a.disconnect()
        # self._config_actions = []

        self._group_actions_by_field = {}

        self._group_filters = []
        self._config_menu.clear()
        self.clear()

    def toggle_action_group_cb(self, *args, **kwargs):
        action = self.sender()
        checked = action.isChecked()
        # self.toggle_action_group(action, self._group_actions_by_field.get(action.text(), []))
        actions = self.actions()
        for a in actions:
            p = a.property("id")
            t = action.text()
            if p == t:
                try:
                    a.defaultWidget().setVisible(checked)
                except:
                    # No worries
                    pass
                a.setVisible(checked)

    def toggle_action_group(self, action, actions):
        checked = action.isChecked()
        for a in actions:
            try:
                a.defaultWidget().setVisible(checked)
            except:
                # No worries
                pass
            a.setVisible(checked)

    def create_filter_item_and_action(self, filter_data):
        """
        """

        filter_item = FilterItem.create(filter_data)

        action = QtGui.QWidgetAction(self.parentWidget())
        widget = FilterItemWidget.create(filter_data)
        widget.filter_item_checked.connect(
            lambda state, a=action: self._filter_item_changed(a, state)
        )
        widget.filter_item_text_changed.connect(
            lambda text, f=filter_item: self._filter_item_text_changed(f, text)
        )

        action.setDefaultWidget(widget)
        action.setCheckable(True)
        action.triggered.connect(
            lambda checked=False, w=widget: self._filter_changed(w)
        )

        return (filter_item, action)

    @property
    def active_filter(self):
        """"""

        return self._active_filter

    @property
    def has_filtering(self):
        """
        Return True if the menu has any active filtering.
        """

        return bool(self._active_filter and self._active_filter.filters)

    def _filter_item_changed(self, action, state):
        """
        """

        action.setChecked(state == QtCore.Qt.Checked)
        self._build_filter()
        self.filters_changed.emit()

    def _filter_item_text_changed(self, filter_item, text):
        """
        """

        filter_item.filter_value = text
        # TODO support multiple values via comma separated list
        # filter_item.filter_value = text.split(",")

        self._build_filter()
        self.filters_changed.emit()

    def _filter_changed(self, filter_menu_item_widget):
        """
        Callback on filter action triggered.

        Rebuild the active filter.
        """

        # Update the filter widget which will then trigger a re-build of the filters and signal emitting
        filter_menu_item_widget.action_triggered()

    def _build_filter(self):
        """"""

        active_group_filters = []

        for filters in self._group_filters:
            active_filters = [
                filter_item
                for filter_item, action in filters
                if action.defaultWidget().has_value()
            ]
            if active_filters:
                active_group_filters.append(
                    (
                        FilterItem(
                            FilterItem.TYPE_GROUP,
                            FilterItem.OP_OR,
                            filters=active_filters,
                        )
                    )
                )

        self._active_filter.filters = active_group_filters

    def clear_filters(self):
        """
        """

        for filters in self._group_filters:
            for _, action in filters:
                # FIXME block signals to avoid retriggering the filter model each time a filter item is cleared -- just do it once at the end
                action.setChecked(False)
                action.defaultWidget().clear_value()

        self._active_filter.filters = []
        self.filters_changed.emit()


class ShotgunFilterMenu(FilterMenu):
    """
    Subclass of FilterMenu. The only thing this class does is it builds the filters based on the given
    entity type to the FilterMenu.
    """

    def __init__(self, shotgun_model, parent, fields=None):
        """
        """

        # FIXME this class needs major clean up -- just exploring how filtering can work right now

        self._invalid_field_types = ["image"]

        self.entity_model = shotgun_model
        # FIXME add logic to rebuild the menu when model data changes
        # self.entity_model.data_refreshed.connect(self.rebuild)

        filters = self.get_entity_filters()

        super(ShotgunFilterMenu, self).__init__(filters, parent, fields)

    def rebuild(self):
        """
        """

        filters = self.get_entity_filters()
        self.build_menu(filters)

    def get_entity_filters(self):
        """
        Return a list of filters for task entity.
        """

        # check if it's a ShotgunModel specifically?
        if not hasattr(self.entity_model, "get_entity_type"):
            return []

        bundle = sgtk.platform.current_bundle()
        if bundle.tank.pipeline_configuration.is_site_configuration():
            # site configuration (no project id). Return None which is
            # consistent with core.
            project_id = None
        else:
            project_id = bundle.tank.pipeline_configuration.get_project_id()

        entity_type = self.entity_model.get_entity_type()
        if not entity_type:
            return []

        fields = shotgun_globals.get_entity_fields(entity_type, project_id=project_id)
        fields.sort()

        filter_data = {}
        self._get_item_filters(
            self.entity_model.invisibleRootItem(),
            entity_type,
            project_id,
            fields,
            filter_data,
        )

        filters = [
            {
                "filter_type": data["type"],
                "filter_op": FilterItem.default_op_for_type(data["type"]),
                "filter_value": data["values"],
                "name": data["name"],
                "data_func": lambda i, f=field: get_index_data(i, f),
                "field": field,
            }
            for field, data in filter_data.items()
        ]

        return filters

    def _get_item_filters(self, item, entity_type, project_id, fields, filter_data):
        """
        """

        for group_row in range(item.rowCount()):
            # entity_item = entity_model.item(group_row)
            entity_item = item.child(group_row)

            # FIXME uncomment to support filtering through all levels in tree model
            # children = entity_item.hasChildren()
            # if children:
            #     self._get_item_filters(entity_item, entity_type, project_id, fields, filter_data)

            sg_data = entity_item.get_sg_data()

            if not sg_data:
                # NOTE this is shotgun data but it's not stored in the SG_DATA_ROLE but rather
                # each item in the model has some of the entity data as a hierarchy.. we could just
                # show ALL fields for the entity
                self._add_item_filter(entity_item, entity_type, filter_data)

            else:
                self._add_sg_field_filter(
                    entity_type, project_id, fields, sg_data, filter_data
                )

    def _add_item_filter(self, item, name, filter_data):
        """
        """
        filter_role = QtCore.Qt.DisplayRole

        # Is it OK to assume this is a string?
        value = item.data(filter_role)

        if filter_role in filter_data:
            filter_data[filter_role]["values"].setdefault(value, {}).setdefault(
                "count", 0
            )
            filter_data[filter_role]["values"][value]["count"] += 1
            filter_data[filter_role]["values"][value]["value"] = value

        else:
            filter_data[filter_role] = {
                # "name": "Non Shotgun Data",  # TEMP
                "name": name,
                "type": FilterItem.TYPE_LIST,
                "values": {value: {"value": value, "count": 1}},
            }

    def _add_sg_field_filter(
        self, entity_type, project_id, fields, sg_data, filter_data
    ):
        """
        """

        for sg_field, value in sg_data.items():
            if sg_field not in fields:
                # if sg_field not in fields or (self._visible_fields and sg_field not in self._visible_fields):
                continue

            field_type = shotgun_globals.get_data_type(
                entity_type, sg_field, project_id
            )
            # if field_type not in valid_field_types:
            if field_type in self._invalid_field_types:
                continue

            field_display = shotgun_globals.get_field_display_name(
                entity_type, sg_field, project_id
            )
            field_id = sg_field

            if isinstance(value, list):
                values_list = value
            else:
                values_list = [value]

            for val in values_list:
                if isinstance(val, dict):
                    # assuming it is an entity dict
                    value_id = val.get("name", str(val))
                    filter_value = val
                elif field_type in (FilterItem.TYPE_DATE, FilterItem.TYPE_DATETIME):
                    datetime_bucket = FilterItem.get_datetime_bucket(value)
                    value_id = datetime_bucket
                    filter_value = datetime_bucket
                else:
                    value_id = val
                    filter_value = val

                if field_id in filter_data:
                    filter_data[field_id]["values"].setdefault(value_id, {}).setdefault(
                        "count", 0
                    )
                    filter_data[field_id]["values"][value_id]["count"] += 1
                    filter_data[field_id]["values"][value_id]["value"] = filter_value
                else:
                    filter_data[field_id] = {
                        "name": field_display,
                        "type": field_type,
                        "values": {value_id: {"value": filter_value, "count": 1}},
                    }

                # TODO icons?
                # filter_data[field]["values"][value]["icon"] = entity_item.model().get_entity_icon(entity_type)


def get_index_data(index, field):
    """
    Callback
    """

    # FIXME more automated way to retrieve shotgun field data from model
    if not index.isValid():
        return None
    item = index.model().item(index.row(), index.column())
    sg_data = item.get_sg_data()
    if sg_data:
        return sg_data.get(field)

    # Non-sg data, the 'field' is the item data role to extract data from the item itself
    return index.data(field)
