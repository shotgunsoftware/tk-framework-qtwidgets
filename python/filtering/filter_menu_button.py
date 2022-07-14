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

from .filter_menu import FilterMenu

sg_qicons = sgtk.platform.current_bundle().import_module("sg_qicons")
SGQIcon = sg_qicons.SGQIcon

sg_qwidgets = sgtk.platform.current_bundle().import_module("sg_qwidgets")
SGQToolButton = sg_qwidgets.SGQToolButton


class FilterMenuButton(SGQToolButton):
    """
    A QToolButton to be used with the FilterMenu class.
    """

    def __init__(self, parent=None, text=None, icon=None):
        """
        Constructor.

        :param parent: The parent widget.
        :type parent: :class:`sgtk.platform.qt.QtGui.QWidget`
        :param text: The text displayed on the button.
        :type text: str
        :param icon: The button icon.
        :type icon: :class:`sgtk.platform.qt.QtGui.QIcon`
        """

        super(FilterMenuButton, self).__init__(parent)

        if not icon:
            icon = SGQIcon.filter()

        self.setCheckable(True)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setIcon(icon)
        self.setText(text or "Filter")

    def setMenu(self, menu):
        """
        Override the QMenu method.

        Enforce the menu to be of type `FilterMenu`. Connect the menu's filters changed
        signal to update the menu button accordingly.
        """

        assert isinstance(
            menu, FilterMenu
        ), "FilterMenuButton menu must be of type '{}'".format(
            FilterMenu.__class__.__name__
        )

        if self.menu():
            self.menu().filters_changed.disconnect(self.update_button_checked)

        super(FilterMenuButton, self).setMenu(menu)

        self.menu().filters_changed.connect(self.update_button_checked)

    def update_button_checked(self):
        """
        Callback triggered when the menu filters have changed. Update the button's checked state
        based on the menu's current filtering.
        """

        # Update the menu button icon to indicate whether or not the menu has any active filtering.
        self.setChecked(self.menu().has_filtering)
