# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import sgtk
from sgtk.platform.qt import QtGui

from .ui import resources_rc


class SGQIcon(QtGui.QIcon):
    """
    The ShotGrid icon class aims to facilitate creating consistent Qt icons in Toolkit.

    This class subclasses QtGui.QIcon but does not intend to provide additional functionality. The main
    purpose is to define factory classmethods to create an icon, which provides a convenience to the caller
    sine they no longer need to know the exact path to the icon resource.

    TODO add all icons used throughout Toolkit here, and provide all pixmap for all modes/state
    TODO rename icon files to reflect exactly which mode (normal, disabled, active, selected) and state (on, off)
    """

    # Enum for icon sizes
    # The pixel dimensions are suggested but not enforced for each size.
    # TODO ensure all icons have all sizes available
    (
        SIZE_16x16,
        SIZE_20x20,
        SIZE_32x32,
        SIZE_40x40,
    ) = range(4)

    # Icon size name (used to get icon resource path)
    SIZES = {
        SIZE_16x16: "16x16",
        SIZE_20x20: "20x20",
        SIZE_32x32: "32x32",
        SIZE_40x40: "40x40",
    }

    def __init__(
        self,
        normal_off,
        normal_on=None,
        disabled_off=None,
        disabled_on=None,
        active_off=None,
        active_on=None,
        selected_off=None,
        selected_on=None,
    ):
        """
        Create a ShotGrid Qt icon object.

        :param normal_off: The icon resource path for normal mode and off state.
        :type normal_off: str
        :param normal_on: The icon resource path for normal mode and on state.
        :type normal_on: str
        :param disabled_off: The icon resource path for disabled mode and off state.
        :type disabled_off: str
        :param disabled_on: The icon resource path for disabled mode and on state.
        :type disabled_on: str
        :param active_off: The icon resource path for active mode and off state.
        :type active_off: str
        :param active_on: The icon resource path for active mode and on state.
        :type active_on: str
        :param selected_off: The icon resource path for selected mode and off state.
        :type selected_off: str
        :param selected_on: The icon resource path for selected mode and on state.
        :type selected_on: str
        """

        super(SGQIcon, self).__init__()

        # The pixmap for the mode Normal and state On is the default
        self.addPixmap(
            QtGui.QPixmap(normal_off),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )

        # Set the following pixmaps for the specified modes and state. If no pixmap is
        # specified, the default pixmap shown for the mode/state will be determined based on
        # which other mode/state pixmaps have been set.

        # If not explicitly set, defaults to Active/On (if set), else Normal/Off
        if normal_on:
            self.addPixmap(
                QtGui.QPixmap(normal_on),
                QtGui.QIcon.Normal,
                QtGui.QIcon.On,
            )

        # If not explicitly set, defaults to Normal/Off
        if disabled_off:
            self.addPixmap(
                QtGui.QPixmap(disabled_off),
                QtGui.QIcon.Disabled,
                QtGui.QIcon.Off,
            )

        # If not explicitly set, defaults to
        # Normal/On (if set), else Disabled/Off (if set), else Normal/Off
        if disabled_on:
            self.addPixmap(
                QtGui.QPixmap(disabled_on),
                QtGui.QIcon.Disabled,
                QtGui.QIcon.On,
            )

        # If not explicitly set, defaults to Normal/Off
        if active_off:
            self.addPixmap(
                QtGui.QPixmap(active_off),
                QtGui.QIcon.Active,
                QtGui.QIcon.On,
            )

        # If not explicitly set, defaults to
        # Normal/On (if set), else Active/Off (if set), else Normal/Off
        if active_on:
            self.addPixmap(
                QtGui.QPixmap(active_on),
                QtGui.QIcon.Active,
                QtGui.QIcon.On,
            )

        # If not explicitly set, defaults to Normal/Off
        if selected_off:
            self.addPixmap(
                QtGui.QPixmap(selected_off),
                QtGui.QIcon.Selected,
                QtGui.QIcon.On,
            )

        # If not explicitly set, defaults to
        # Normal/On (if set), else Selected/Off (if set), else Normal/Off
        if selected_on:
            self.addPixmap(
                QtGui.QPixmap(selected_on),
                QtGui.QIcon.Selected,
                QtGui.QIcon.On,
            )

    @classmethod
    def resource_path(cls, name, size, ext="png"):
        """
        Convenience method to get the resource path for an icon.

        :param name: The file name of the icon (not including the size suffix or file extension).
        :type name: str
        :param size: The icon size suffix (indicating which icon size to use). Should be one of:
            'SIZE_16x16', SIZE_32x32', 'SIZE_40x40'
        :type size: str
        :param ext: The file extension for the icon. Default='png'
        :type ext: str
        """

        return ":/tk-framework-qtwidgets/icons/{icon_name}_{sz}.{ext}".format(
            icon_name=name,
            sz=cls.SIZES.get(size, cls.SIZE_20x20),
            ext=ext,
        )

    ##########################################################################################################
    # Factory class methods to create specific Toolkit icons
    ##########################################################################################################
    # TODO add a classmethod to create all icons used in Toolkit
    #

    @classmethod
    def validation_ok(cls, size=SIZE_20x20):
        icon = cls.resource_path("validation_ok", size)
        return cls(icon)

    @classmethod
    def validation_warning(cls, size=SIZE_20x20):
        icon = cls.resource_path("validation_warning", size)
        return cls(icon)

    @classmethod
    def validation_error(cls, size=SIZE_20x20):
        icon = cls.resource_path("validation_error", size)
        return cls(icon)

    @classmethod
    def red_refresh(cls, size=SIZE_20x20):
        icon = cls.resource_path("refresh_red", size)
        return cls(icon)

    @classmethod
    def grey_refresh(cls, size=SIZE_20x20):
        icon = cls.resource_path("refresh_grey", size)
        return cls(icon)

    @classmethod
    def transparent_refresh(cls, size=SIZE_20x20):
        icon = cls.resource_path("refresh", size)
        return cls(icon)

    @classmethod
    def refresh(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("refresh-inactive", size),
            normal_on=cls.resource_path("refresh-active", size),
            disabled_off=cls.resource_path("refresh-inactive-disabled", size),
            disabled_on=cls.resource_path("refresh-active-disabled", size),
        )

    @classmethod
    def red_bullet(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("bullet_inactive", size),
            normal_on=cls.resource_path("bullet_active", size),
        )

    @classmethod
    def lock(cls, size=SIZE_20x20):
        icon = cls.resource_path("lock", size)
        return cls(icon)

    @classmethod
    def green_check_mark(cls, size=SIZE_20x20):
        icon = cls.resource_path("check_mark_green", size)
        return cls(icon)

    @classmethod
    def red_check_mark(cls, size=SIZE_20x20):
        icon = cls.resource_path("check_mark_red", size)
        return cls(icon)

    @classmethod
    def filter(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("filter-inactive", size),
            normal_on=cls.resource_path("filter-active", size),
            disabled_off=cls.resource_path("filter-inactive-disabled", size),
            disabled_on=cls.resource_path("filter-active-disabled", size),
        )

    @classmethod
    def info(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("info_inactive", size),
            normal_on=cls.resource_path("info_active", size),
        )

    @classmethod
    def tree_arrow(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("tree_arrow_expanded", size),
            normal_on=cls.resource_path("tree_arrow_collapsed", size),
        )

    @classmethod
    def list_view_mode(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("view_list_inactive", size),
            normal_on=cls.resource_path("view_list_active", size),
        )

    @classmethod
    def thumbnail_view_mode(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("view_thumbnail_inactive", size),
            normal_on=cls.resource_path("view_thumbnail_active", size),
        )

    @classmethod
    def grid_view_mode(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("view_grid_inactive", size),
            normal_on=cls.resource_path("view_grid_active", size),
        )

    @classmethod
    def toggle(cls, size=SIZE_20x20):
        return cls(
            normal_off=cls.resource_path("toggle_inactive", size),
            normal_on=cls.resource_path("toggle_active", size),
        )
