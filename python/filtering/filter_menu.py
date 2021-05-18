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


class FilterMenu(ShotgunMenu):
    """"""

    filters_changed = QtCore.Signal()

    def __init__(self, filters, parent):
        """
        Constructor
        """

        super(FilterMenu, self).__init__(parent)
        self.build_menu(filters)

    def build_menu(self, filters):
        """
        """

        self._group_filters = []

        for filter_group in filters:
            actions = []
            filters = []

            filter_defs = filter_group.get("filters", [])
            if not filter_defs:
                # FIXME handle filter widgets based on type better than this
                if filter_group.get("filter_type") == FilterItem.TYPE_NUMBER:
                    filter_defs.append(
                        {
                            "filter_type": filter_group.get("filter_type"),
                            "filter_op": filter_group.get("filter_op"),
                            "data_func": filter_group.get("data_func"),
                            # "filter_value": filter_value.get("value"),
                            # "display_name": filter_value.get("name", str(filter_name)),
                            # "count": filter_value.get("count", 0)
                        }
                    )

                else:
                    for filter_name, filter_value in filter_group.get(
                        "filter_value", {}
                    ).items():
                        # FIXME
                        filter_defs.append(
                            {
                                "filter_type": filter_group.get("filter_type"),
                                "filter_op": filter_group.get("filter_op"),
                                "data_func": filter_group.get("data_func"),
                                "filter_value": filter_value.get("value"),
                                "display_name": filter_value.get(
                                    "name", str(filter_name)
                                ),
                                "count": filter_value.get("count", 0),
                            }
                        )

            # for filter_def in filter_group.get("filters", []):
            for filter_def in filter_defs:
                filter_item = FilterItem.create(filter_def)

                # action = QtGui.QWidgetAction(parent)
                action = QtGui.QWidgetAction(self.parentWidget())
                widget = FilterItemWidget.create(filter_def)
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
                # TODO add init option to set the filter on creation

                filters.append((filter_item, action))
                actions.append(action)

            self._group_filters.append(filters)

            sorted_actions = sorted(actions, key=lambda item: item.text())
            self.add_group(sorted_actions, filter_group.get("name"))

        self._active_filter = FilterItem(
            FilterItem.TYPE_GROUP, FilterItem.OP_AND, filters=[]
        )

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

        # Update the filter widget
        # FIXME this causes checkbox signal to trigger
        filter_menu_item_widget.action_triggered()

        # FIXME naively just goes through all filters, instead of just modifying the oen that changed
        # self._build_filter()

        # self.filters_changed.emit()

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


class ShotgunFilterMenu(FilterMenu):
    """
    Subclass of FilterMenu. The only thing this class does is it builds the filters based on the given
    entity type to the FilterMenu.
    """

    def __init__(self, shotgun_model, parent):
        """
        """

        filters = self.get_entity_filters(shotgun_model)
        super(ShotgunFilterMenu, self).__init__(filters, parent)

    @staticmethod
    def get_entity_filters(entity_model):
        """
        Return a list of filters for task entity.
        """

        # check if it's a ShotgunModel specifically?
        if not hasattr(entity_model, "get_entity_type"):
            return []

        bundle = sgtk.platform.current_bundle()
        if bundle.tank.pipeline_configuration.is_site_configuration():
            # site configuration (no project id). Return None which is
            # consistent with core.
            project_id = None
        else:
            project_id = bundle.tank.pipeline_configuration.get_project_id()

        # TODO assert it is a shotgun model and has this method to get the entity type
        entity_type = entity_model.get_entity_type()

        entity_type = entity_model.get_entity_type()
        fields = shotgun_globals.get_entity_fields(entity_type, project_id=project_id)
        fields.sort()

        # TODO configure these via param or something
        valid_field_types = [
            "text",
            "number",
            "status_list",
        ]
        invalid_field_types = ["image"]

        # FIXME more automated way to retrieve shotgun field data from model
        def get_index_field_data(index, sg_field):
            if not index.isValid():
                return None
            item = index.model().item(index.row(), index.column())
            sg_data = item.get_sg_data()
            return sg_data.get(sg_field)

        filter_data = {}

        for group_row in range(entity_model.rowCount()):
            entity_item = entity_model.item(group_row)
            sg_data = entity_item.get_sg_data()

            # FIXME if this is a group header.. it has no sg data - but its children do..
            if not sg_data:
                continue

            for field, value in sg_data.items():
                if field not in fields:
                    continue

                field_type = shotgun_globals.get_data_type(
                    entity_type, field, project_id
                )
                # if field_type not in valid_field_types:
                if field_type in invalid_field_types:
                    continue

                field_display = shotgun_globals.get_field_display_name(
                    entity_type, field, project_id
                )
                field_id = field

                if isinstance(value, list):
                    values_list = value
                else:
                    values_list = [value]

                for val in values_list:
                    if isinstance(val, dict):
                        # assuming it is an entity dict
                        value_id = val.get("name", str(val))
                        field_display = "{} {}".format(
                            shotgun_globals.get_type_display_name(
                                val.get("type"), project_id
                            ),
                            field_display,
                        )
                    else:
                        value_id = val

                    if field_id in filter_data:
                        filter_data[field_id]["values"].setdefault(
                            value_id, {}
                        ).setdefault("count", 0)
                        filter_data[field_id]["values"][value_id]["count"] += 1
                        filter_data[field_id]["values"][value_id]["value"] = val
                    else:
                        filter_data[field_id] = {
                            "name": field_display,
                            "type": field_type,
                            "values": {value_id: {"value": val, "count": 1}},
                        }
                    # TODO icons?
                    # filter_data[field]["values"][value]["icon"] = entity_item.model().get_entity_icon(entity_type)

        filters = [
            {
                # "filter_type": FilterItem.TYPE_LIST,
                "filter_type": data["type"],
                "filter_op": FilterItem.OP_EQUAL,
                # "filter_value": data["values"].keys(),
                "filter_value": data["values"],
                "name": data["name"],
                "data_func": lambda i, f=field: get_index_field_data(i, f),
            }
            for field, data in filter_data.items()
        ]
        return filters
