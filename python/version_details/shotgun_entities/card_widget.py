# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from __future__ import with_statement

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.card_widget import Ui_ShotgunEntityCardWidget

import threading

utils = sgtk.platform.import_framework("tk-framework-shotgunutils", "utils")

class ShotgunEntityCardWidget(QtGui.QWidget):
    """
    Simple entity widget which hosts a thumbnail, plus any requested
    entity fields in a layout to the right of the thumbnail.
    """
    WIDTH_HINT = 300
    HEIGHT_HINT_PADDING = 8
    ROW_HEIGHT = 20

    def __init__(self, parent, shotgun_field_manager=None, editable=True):
        """
        Constructs a new ShotgunEntityCardWidget.

        :param parent: The widget's parent.
        :param shotgun_field_manager: A ShotgunFieldManager object. If one is not provided
                                      the widget will not construct field widgets until one
                                      is set later via the field_manager property.
        """
        super(ShotgunEntityCardWidget, self).__init__(parent)

        self.ui = Ui_ShotgunEntityCardWidget() 
        self.ui.setupUi(self)

        self._field_manager = shotgun_field_manager

        self._entity = None
        self._show_border = False
        self._show_labels = True
        self._editable = editable
        self.__selected = False

        self._fields = _OrderedDict()
        self.set_selected(self.__selected)

    ##########################################################################
    # public methods

    def add_field(self, field_name, label_exempt=False):
        """
        Adds the given field to the list of Shotgun entity fields displayed
        by the widget.

        :param str field_name: The Shotgun entity field name to add.
        :param bool label_exempt: Whether to exempt the field from having a label
                                  in the item layout. Defaults to False.
        """
        if not self.field_manager:
            raise RuntimeError(
                "No ShotgunFieldManager has been set, unable to add fields."
            )

        if field_name in self.fields:
            return

        self._fields[field_name] = _OrderedDict(
            widget=None,
            label=None,
            label_exempt=label_exempt,
            row=0,
        )

        # If we've not yet loaded an entity, then we don't need to
        # do any widget work.
        if not self.entity:
            return

        if self.editable:
            widget_type = self.field_manager.EDITABLE
        else:
            widget_type = self.field_manager.DISPLAY

        field_widget = self.field_manager.create_widget(
            self.entity.get("type"),
            field_name,
            widget_type,
            self.entity,
        )

        self._fields[field_name]["widget"] = field_widget

        # Connect each widget to the local value_changed function
        # so we can update the DB.
        if self.editable:
            field_widget.value_changed.connect(self._value_changed)

        if self.show_labels:
            # If this field is exempt from having a label, then it
            # goes into the layout in column 0, but with the column
            # span set to -1. This will cause it to occupy all of the
            # space on this row of the layout instead of just the first
            # column.
            if field_name in self.label_exempt_fields:
                # If there's no label, then the widget goes in the first
                # column and is set to span all columns.
                self.ui.field_grid_layout.addWidget(field_widget, len(self.fields), 0, 1, -1)
            else:
                # We have a label, so we put that in column 0 and the
                # field widget in column 1.
                field_label = self.field_manager.create_label(
                    self.entity.get("type"),
                    field_name,
                    postfix=":",
                )
                self._fields[field_name]["label"] = field_label
                self.ui.field_grid_layout.addWidget(field_label, len(self.fields), 0, QtCore.Qt.AlignRight)
                self.ui.field_grid_layout.addWidget(field_widget, len(self.fields), 1)
        else:
            # Nothing at all will have labels, so we can just put the
            # widget into column 0. No need to worry about telling it to
            # span any additional columns, because there will only be a
            # single column.
            self.ui.field_grid_layout.addWidget(field_widget, len(self.fields), 0)

        self.ui.field_grid_layout.setRowMinimumHeight(len(self.fields), self.ROW_HEIGHT)
        self._fields[field_name]["row"] = len(self.fields)

    def clear(self):
        """
        Clears all data out of the widget.
        """
        if self.entity:
            self._entity = None
            self.clear_fields()
            self.thumbnail.hide()
            self.ui.left_layout.removeWidget(self.thumbnail)
            self.ui.left_layout.update()
            self.thumbnail = None

    def clear_fields(self):
        """
        Removes all field widgets from the item.
        """
        field_names = self.fields

        for field_name in field_names:
            self.destroy_field(field_name)
        self._fields = _OrderedDict()

    def get_visible_fields(self):
        """
        Returns a list of field names that are currently visible.
        """
        # If we have no entity, we have no widgets. If we have no widgets
        # then we definitely don't have anything visible.
        if not self.entity:
            return []

        return [f for f, d in self._fields.iteritems() if d["widget"].isVisible()]

    def destroy_field(self, field_name):
        """
        Cleans up the field widget and its label (when present) for the
        given field name.

        :param str field_name: The Shotgun field name to remove.
        """
        if field_name not in self.fields:
            return

        # Now ditch the widget for the field if we have one. If we
        # don't then we have nothing to worry about.
        try:
            field_widget = self._fields[field_name]["widget"]
        except KeyError:
            return

        if not field_widget:
            return

        field_widget.hide()
        self.ui.field_grid_layout.removeWidget(field_widget)
        field_widget.setParent(None)
        utils.safe_delete_later(field_widget)

        # If there's a label, then also remove that.
        field_label = self._fields[field_name]["label"]

        if field_label:
            field_label.hide()
            self.ui.field_grid_layout.removeWidget(field_label)
            field_label.setParent(None)
            utils.safe_delete_later(field_label)

        self.ui.field_grid_layout.setRowMinimumHeight(
            self._fields[field_name]["row"],
            0,
        )

    def remove_field(self, field_name):
        """
        # Cleans up the given field and removes it from fields.
        """
        self.destroy_field(field_name)
        del self._fields[field_name]

    def set_field_visibility(self, field_name, state):
        """
        Sets the visibility of a field widget by name.

        :param str field_name: The name of the Shotgun field.
        :param bool state: Whether to set the field as visible or not.
        """
        if not self.field_manager:
            return

        # If the field isn't registered with the item or if we've
        # not loaded an entity, then there's nothing to do.
        if field_name not in self._fields or not self.entity:
            return

        if self._fields[field_name]["widget"]: 
            self._fields[field_name]["widget"].setVisible(bool(state))

        field_label = self._fields[field_name]["label"]

        if field_label:
            field_label.setVisible(bool(state))

        if state:
            row_height = self.ROW_HEIGHT
        else:
            row_height = 0

        self.ui.field_grid_layout.setRowMinimumHeight(
            self._fields[field_name]["row"],
            row_height,
        )
                   
    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not.

        :param bool selected: Whether the widget is selected or not.
        """
        p = QtGui.QPalette()

        self.__selected = selected
        
        if selected:
            highlight_col = p.color(QtGui.QPalette.Active, QtGui.QPalette.Highlight)
            highlight_str = "rgb(%s, %s, %s)" % (
                highlight_col.red(),
                highlight_col.green(),
                highlight_col.blue(),
            )

            self.ui.box.setStyleSheet(
                """
                #box {
                    border: 1px solid %s;
                    margin-bottom: 2px;
                    margin-right: 2px;
                }
                """ % (highlight_str)
            )
        elif self._show_border:
            self.ui.box.setStyleSheet(
                """
                #box {
                    border: 1px solid rgb(50,50,50);
                    margin-bottom: 2px;
                    margin-right: 2px;
                }
                """
            )
        else:
            self.ui.box.setStyleSheet("")

    ##########################################################################
    # widget sizing

    def sizeHint(self):
        """
        Tells Qt what the sizeHint for the widget is, based on
        the number of visible field widgets.
        """
        return QtCore.QSize(
            ShotgunEntityCardWidget.WIDTH_HINT,
            self.ui.field_grid_layout.sizeHint().height() + ShotgunEntityCardWidget.HEIGHT_HINT_PADDING,
        )

    def minimumSizeHint(self):
        """
        Tells Qt what the minimumSizeHint for the widget is, based on
        the number of visible field widgets.
        """
        return self.sizeHint()

    ##########################################################################
    # property getters/setters

    def _get_entity(self):
        """
        The widget's current Shotgun entity, or None.
        """
        return self._entity

    def _set_entity(self, entity):
        if not self.field_manager:
            raise RuntimeError(
                "No ShotgunFieldManager has been set, unable to set entity."
            )

        # Don't bother if it's the same entity we already have.
        if self.entity and self.entity == entity:
            return

        # If we've already been populated previously, then we will
        # set the values of the existing field widgets. Otherwise
        # this is a first-time setup and we need to create and place
        # the field widgets into the layout.
        try:
            self.setUpdatesEnabled(False)

            if self.entity:
                self._entity = entity
                self.thumbnail.set_value(entity.get("image"))
                self.thumbnail.setMinimumWidth(150)

                for field, field_data in self._fields.iteritems():
                    field_widget = field_data["widget"]

                    if field_widget:
                        # We need to block signals, otherwise the set_value will kick
                        # off a value_changed signal, which will trigger us to try to
                        # update Shotgun with the "new" value.
                        try:
                            field_widget.blockSignals(True)
                            field_widget.set_value(entity.get(field))
                        finally:
                            field_widget.blockSignals(False)
            else:
                self._entity = entity
                self.thumbnail = self.field_manager.create_widget(
                    entity.get("type"),
                    "image",
                    self.field_manager.DISPLAY,
                    self.entity,
                )
                self.thumbnail.setMinimumWidth(150)

                # The stretch factor helps the item widget scale horizontally
                # in a sane manner while generally pushing the field grid
                # layout toward the thumbnail on the left.
                self.ui.box_layout.setStretchFactor(self.ui.right_layout, 6)
                self.ui.box_layout.setStretchFactor(self.ui.left_layout, 2)
                self.ui.left_layout.insertWidget(0, self.thumbnail)

                # Visually, this will just cause column 1 of the grid layout
                # to fill any remaining space to the right of the grid within
                # the parent layout.
                field_grid_layout = self.ui.field_grid_layout
                field_grid_layout.setColumnStretch(1, 3)

                if self.editable:
                    widget_type = self.field_manager.EDITABLE
                else:
                    widget_type = self.field_manager.DISPLAY

                for i, field in enumerate(self.fields):
                    field_widget = self.field_manager.create_widget(
                        entity.get("type"),
                        field,
                        widget_type,
                        self.entity,
                    )
                    # Connect each widget to the local value_changed function
                    # so we can update the DB.
                    if self.editable:
                        field_widget.value_changed.connect(self._value_changed)

                    # If we've been asked to show labels for the fields, then
                    # build those and get them into the layout.
                    if self.show_labels:
                        # If this field is exempt from having a label, then it
                        # goes into the layout in column 0, but with the column
                        # span set to -1. This will cause it to occupy all of the
                        # space on this row of the layout instead of just the first
                        # column.
                        if field in self.label_exempt_fields:
                            field_grid_layout.addWidget(field_widget, i, 0, 1, -1)
                        else:
                            field_label = self.field_manager.create_label(
                                entity.get("type"),
                                field,
                                postfix=":",
                            )

                            field_grid_layout.addWidget(field_label, i, 0, QtCore.Qt.AlignRight)
                            self._fields[field]["label"] = field_label
                            field_grid_layout.addWidget(field_widget, i, 1)
                    else:
                        field_grid_layout.addWidget(field_widget, i, 0)

                    field_grid_layout.setRowMinimumHeight(i, self.ROW_HEIGHT)

                    self._fields[field]["widget"] = field_widget
                    self._fields[field]["row"] = i
        finally:
            self.setUpdatesEnabled(True)

    def _value_changed(self):
        """
        All field widgets created in this class will call this function when their
        editor emits a value_changed signal. We just call update from the bundle's
        Shotgun instance so this function is blocking for now.
        """
        entity = self._get_entity()

        update_dict = {}
        update_dict[self.sender().get_field_name()] = self.sender().get_value()

        bundle = sgtk.platform.current_bundle()
        sg_res = bundle.shotgun.update(entity['type'], entity['id'], update_dict)

    def _get_field_manager(self):
        """
        The widget's :class:`~ShotgunFieldManager`.
        """
        return self._field_manager

    def _set_field_manager(self, manager):
        # We keep track of the manager, but then we also need to trigger
        # the creation (or recreation) of the widgets for all of the
        # fields that we have. The quickest way to do that is to just
        # reset the fields property to the same list of field names. That
        # will clear any existing fields data we have and trigger the
        # creation of widgets for those fields using the new field manager.
        self._field_manager = manager
        self.fields = self.fields

    def _get_fields(self):
        """
        A list of field names currently registered with the item.
        """
        return self._fields.keys()

    def _set_fields(self, fields):
        label_exempt = self.label_exempt_fields
        self.clear_fields()
        for field_name in fields:
            self.add_field(
                field_name,
                label_exempt=(field_name in label_exempt),
            )

    def _get_label_exempt_fields(self):
        """
        A list of field names that are exempt from receiving labels in the
        item's layout.
        """
        return [f for f, d in self._fields.iteritems() if d["label_exempt"]]

    def _set_label_exempt_fields(self, fields):
        fields_to_add = {}
        for field_name, field_data in self._fields.iteritems():
            now_exempt = (field_name in fields)

            if self.entity:
                previously_exempt = field_data["label_exempt"]

                # If the state is changing for this field, then we
                # need to rebuild its widgets in the layout.
                if previously_exempt != now_exempt:
                    self.destroy_field(field_name)
                    fields_to_add[field_name] = now_exempt
            else:
                self._fields[field_name]["label_exempt"] = now_exempt

        for field_name in fields_to_add:
            self.add_field(field_name, label_exempt=fields_to_add[field_name])

    def _get_show_labels(self):
        """
        Whether labels are shown for field widgets displayed by the
        item.
        """
        return self._show_labels

    def _set_show_labels(self, state):
        if bool(state) == self._show_labels:
            return

        self._show_labels = bool(state)

        if not self.entity:
            return

        # Re-add all of the current fields. This will cause the item to
        # clear its fields list and rebuild the layout. Since _show_labels
        # will be False when this happens, we will end up in the correct
        # state.
        self._show_labels = bool(state)
        current_fields = self.fields
        self.fields = current_fields

    def _get_show_border(self):
        """
        Whether to show a border line around the edge of the widget when
        it is not selected.
        """
        return self._show_border

    def _set_show_border(self, state):
        self._show_border = bool(state)
        # Resetting the same selection state will force the qss to be
        # reapplied including or omitting the border, as necessary.
        self.set_selected(self.__selected)

    ##########################################################################
    # properties

    @property
    def editable(self):
        """
        Whether the entity card widget contains editable Shotgun fields widgets.
        """
        return self._editable

    @property
    def field_widgets(self):
        """
        A list of field widget objects that are present in the item widget.
        """
        widgets = []
        for field, data in self.fields.iteritems():
            if "widget" in data:
                widgets.append(data["widget"])
        return widgets

    entity = property(_get_entity, _set_entity)
    fields = property(_get_fields, _set_fields)
    field_manager = property(_get_field_manager, _set_field_manager)
    label_exempt_fields = property(_get_label_exempt_fields, _set_label_exempt_fields)
    show_border = property(_get_show_border, _set_show_border)
    show_labels = property(_get_show_labels, _set_show_labels)


class _OrderedDict(object):
    """
    An OrderedDict-like class. This is implemented here in order to maintain
    backwards compatibility with pre-2.7 releases of Python.
    """

    def __init__(self, **kwargs):
        """
        Constructor. Emulates the behavior of the dict() type.

        .. Note:: The order of key/value pairs passed in as kwargs to the
                  constructor will not have their order maintained. This is
                  consistent with the behavior of collections.OrderedDict in
                  Python 2.7.
        """
        self._keys = []
        self._dict = dict()

        for (key, value) in kwargs.iteritems():
            self.__setitem__(key, value)

    def get(self, key, default=None):
        """
        Emulates dict.get()

        :param key: The key to get the value of.
        :param default: What to return if the key isn't in the dictionary.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def iteritems(self):
        """
        Emulates dict.iteritems()
        """
        return [(k, self[k]) for k in self._keys]

    def keys(self):
        """
        Emulates dict.keys()
        """
        return self._keys

    def values(self):
        """
        Emulates dict.values()
        """
        return [self[k] for k in self._keys]

    def __iter__(self):
        for key in self._keys:
            yield self._dict[key]

    def __len__(self):
        return len(self._keys)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._keys.append(key)
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]
        self._keys.remove(key)

    def __contains__(self, item):
        return (item in self._dict)

