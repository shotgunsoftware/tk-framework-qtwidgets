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

        self.__icon = icon if icon else SGQIcon.filter()
        self.__checked = False

        # Set up the animated refresh icon to display while the filter menu for this filter
        # button is loading. Ensure the animation loops forever.
        refresh_icon_path = SGQIcon.resource_path(
            "spinning-wheel", SGQIcon.SIZE_16x16, "gif"
        )
        self.__refresh_movie_icon = QtGui.QMovie(refresh_icon_path)
        if self.__refresh_movie_icon.loopCount() != -1:
            self.__refresh_movie_icon.finished.connect(self.__refresh_movie_icon.start)

        self.setCheckable(True)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setIcon(self.__icon)
        self.setText(text or "Filter")

    def setMenu(self, menu):
        """
        Override the base QToolButton method.

        Enforce the menu to be of type `FilterMenu`. Connect the menu's filters changed
        signal to update the menu button accordingly.
        """

        assert isinstance(
            menu, FilterMenu
        ), "FilterMenuButton menu must be of type '{}'".format(
            FilterMenu.__class__.__name__
        )

        if self.menu():
            self.menu().menu_about_to_be_refreshed.disconnect(
                lambda: self.set_enabled(False)
            )
            self.menu().menu_refreshed.disconnect(lambda: self.set_enabled(True))
            self.menu().filters_changed.disconnect(self.update_button_checked)

        super(FilterMenuButton, self).setMenu(menu)
        self.update_button_checked()

        self.menu().filters_changed.connect(self.update_button_checked)
        self.menu().menu_about_to_be_refreshed.connect(lambda: self.set_enabled(False))
        self.menu().menu_refreshed.connect(lambda: self.set_enabled(True))

    def setEnabled(self, enabled):
        """Override the base QToolButton method to ensure the check state is restored."""

        super(FilterMenuButton, self).setEnabled(enabled)

        if not enabled:
            # Uncheck the button while disabled so stylistically it looks disabled.
            self.setChecked(False)
        else:
            # Restore the check state on enabling it again.
            self.setChecked(self.__checked)

    def update_button_checked(self):
        """
        Callback triggered when the menu filters have changed. Update the button's checked state
        based on the menu's current filtering.
        """

        self.__checked = self.menu().has_filtering

        if self.isEnabled():
            # Update the menu button icon to indicate whether or not the menu has any active
            # filtering. Do not update the check state while not enabled, since this may
            # override the disabled icon. Restore the check state once button is enabled.
            self.setChecked(self.__checked)

    def set_enabled(self, enabled):
        """
        Update the button enabled state.

        :param enabled: True will turn on the button (enable), else False will turn off (disable).
        :type enabled: bool
        """

        self.setEnabled(enabled)

        if not enabled:
            # Show the animated refresh icon. Connect the animation signal/slot.
            self.__refresh_movie_icon.frameChanged.connect(self._update_refresh_icon)
            self.__refresh_movie_icon.start()
        else:
            # Show the main button icon and stop the refresh animation
            self.setIcon(self.__icon)
            self.__refresh_movie_icon.stop()

            # Disconnect the animation signal/slot
            try:
                self.__refresh_movie_icon.frameChanged.disconnect(
                    self._update_refresh_icon
                )
            except:
                # Signal was not connected, continue on.
                pass

    def _update_refresh_icon(self, frame):
        """Update the animated refresh icon."""

        self.setIcon(QtGui.QIcon(self.__refresh_movie_icon.currentPixmap()))
