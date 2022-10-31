# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

from enum import Enum

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from tank_vendor import six

sg_qwidgets = sgtk.platform.current_bundle().import_module("sg_qwidgets")


class NodeGraphDetailsWidget(sg_qwidgets.SGQWidget):
    """Widget displays the details for a node in a graph widget."""

    def __init__(self, parent=None):
        """
        Create the optimize details widget.

        :param parent: The parent widget
        :type parent: QtGui.QWidget
        """

        super(NodeGraphDetailsWidget, self).__init__(
            parent, layout_direction=QtGui.QBoxLayout.TopToBottom
        )

        self.__item = None

        self.__setup_ui()
        self.__connect_signals()

    #########################################################################################################
    # Properties

    @property
    def item(self):
        """Get the current node displayed in the details."""
        return self.__item

    ######################################################################################################
    # Public methods

    def set_data(self, node):
        """
        Set up the details data for the given graph node.

        :param node: The node that the details is showing information for.
        :type node: NOde
        """

        self.__item = node
        self.refresh()

    def clear(self):
        """Clear the details."""

        self.__details.setTitle("")
        self.__details_description.setText("")
        self.__settings_widget.clear()

    def refresh(self):
        """Refresh the current data in the widget."""

        self.clear()

        if not self.item:
            # TODO use overlay
            return

        self.__details.setTitle(self.item.name)
        self.__details_description.setText(self.item.description)

        # TODO add reset to default settings button

        # Add the editable settings widgets
        # TODO add header label for settings?
        settings_widgets = []
        for setting_id, setting_value in self.item.settings.items():
            # First add the settings label
            label = sg_qwidgets.SGQLabel(self)
            label_text = "{label}: ".format(label=setting_value["name"])
            label.setText(label_text)

            # Next, add the settings editable value widget
            # TODO update values when user edits
            setting_type = setting_value["type"]
            value = setting_value.get("value", setting_value.get("default"))

            if setting_type in (str, int, float):
                # Add a line edit for the text setting
                value_widget = sg_qwidgets.SGQLineEdit(self)

                if setting_type is int:
                    int_validator = QtGui.QIntValidator(self)
                    if "min" in setting_value:
                        int_validator.setBottom(setting_value["min"])
                    if "max" in setting_value:
                        int_validator.setBottom(setting_value["max"])
                    value_widget.setValidator(int_validator)
                elif setting_type is float:
                    double_validator = QtGui.QDoubleValidator(self)
                    if "min" in setting_value:
                        double_validator.setBottom(setting_value["min"])
                    if "max" in setting_value:
                        double_validator.setBottom(setting_value["max"])
                    if "decimals" in setting_value:
                        double_validator.setDecimals(setting_value["decimals"])
                    value_widget.setValidator(double_validator)

                if value is not None:
                    if not isinstance(value, six.string_types):
                        value = str(value)
                    value_widget.setText(value)

                value_widget.editingFinished.connect(
                    lambda w=value_widget, s=setting_id: self.__on_settings_changed(
                        w, s
                    )
                )

            elif setting_type is Enum:
                # Add a combobox with the list of choices for the enum type
                value_widget = sg_qwidgets.SGQComboBox(self)

                # Add the choices to the combobox
                current_text = None
                for choice_name, choice_value in setting_value.get("choices", []):
                    value_widget.addItem(choice_name, choice_value)
                    if value == choice_value:
                        current_text = choice_name

                if current_text is not None:
                    value_widget.setCurrentText(current_text)

                value_widget.currentIndexChanged.connect(
                    lambda index, w=value_widget, s=setting_id: self.__on_settings_changed(
                        w, s
                    )
                )

            elif setting_type is bool:
                # Add a checkbox for hte boolean setting
                value_widget = sg_qwidgets.SGQCheckBox(self)
                checked = bool(value)
                value_widget.setChecked(checked)
                value_widget.stateChanged.connect(
                    lambda state, w=value_widget, s=setting_id: self.__on_settings_changed(
                        w, s
                    )
                )

            else:
                raise Exception(
                    "Settings value type not supported '{}'".format(setting_type)
                )

            setting_widget = sg_qwidgets.SGQWidget(
                self, child_widgets=[label, value_widget, None]
            )
            settings_widgets.append(setting_widget)

        settings_widgets.append(None)
        self.__settings_widget.add_widgets(settings_widgets)

    ######################################################################################################
    # Private methods

    def __setup_ui(self):
        """
        Set up the widget UI.

        This should be called once when creating the widget.
        """

        self.__details = sg_qwidgets.SGQGroupBox(self)
        self.__details.setMinimumWidth(200)
        self.__details.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        )
        self.__details_description = sg_qwidgets.SGQLabel(self.__details)
        self.__details_description.setWordWrap(True)
        details_vlayout = QtGui.QVBoxLayout()
        details_vlayout.addWidget(self.__details_description)
        self.__details.setLayout(details_vlayout)

        self.__details_toolbar = sg_qwidgets.SGQWidget(self)
        self.__settings_widget = sg_qwidgets.SGQWidget(
            self, layout_direction=QtGui.QBoxLayout.TopToBottom
        )

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.add_widgets(
            [self.__details, self.__details_toolbar, self.__settings_widget]
        )

    def __connect_signals(self):
        """
        Set up and connect signal slots between widgets.

        This should be called once when creating the widget.
        """

    ######################################################################################################
    # Callback methods

    def __on_settings_changed(self, setting_widget, setting_id):
        """Callback triggered when the current node settings have been changed."""

        if not setting_widget or not self.item:
            return

        if isinstance(setting_widget, QtGui.QLineEdit):
            value = setting_widget.text()

        elif isinstance(setting_widget, QtGui.QCheckBox):
            value = setting_widget.isChecked()

        elif isinstance(setting_widget, QtGui.QComboBox):
            value = setting_widget.currentData()

        else:
            # TODO add custom exception class and better message
            raise Exception("Unsupported setting widget type")

        # Updating the value may change the bounding box of the node
        self.item.prepareGeometryChange()
        self.item.settings[setting_id]["value"] = value
