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

    TODO add all icons used throughout Toolkit here.
    TODO support all modes for a QIcon (Active, Disabled, Selected)
    """

    # Enum for icon sizes
    # The pixel dimensions are suggested but not enforced for each size.
    # NOTE that not all icons will be available in all sizes.
    (SMALL, MEDIUM, LARGE, EXTRA_LARGE,) = range(
        4
    )  # 16x16  # 20x20  # 32x32  # 40x40

    # Icon size name (used to get icon resource path)
    SIZES = {
        SMALL: "small",
        MEDIUM: "medium",
        LARGE: "large",
        EXTRA_LARGE: "extra_large",
    }

    def __init__(self, normal_off=None, normal_on=None):
        """
        Create a ShotGrid Qt icon object.

        :param normal_off: The icon resource path for normal mode and off state.
        :type normal_off: str
        :param normal_on: The icon resource path for normal mode and on state.
        :type normal_on: str
        """

        super(SGQIcon, self).__init__()

        if normal_off:
            self.addPixmap(
                QtGui.QPixmap(normal_off),
                QtGui.QIcon.Normal,
                QtGui.QIcon.Off,
            )

        if normal_on:
            self.addPixmap(
                QtGui.QPixmap(normal_on),
                QtGui.QIcon.Normal,
                QtGui.QIcon.On,
            )

    @classmethod
    def resource_path(cls, name, size, ext="png"):
        """
        Convenience method to get the resource path for an icon.

        :param name: The file name of the icon (not including the size suffix or file extension).
        :type name: str
        :param size: The icon size suffix (indicating which icon size to use). Should be one of:
            'small', 'medium', 'large', 'extra_large'
        :type size: str
        :param ext: The file extension for the icon. Default='png'
        :type ext: str
        """

        return ":/tk-framework-qtwidgets/icons/{icon_name}_{sz}.{ext}".format(
            icon_name=name,
            sz=cls.SIZES.get(size, cls.MEDIUM),
            ext=ext,
        )

    ##########################################################################################################
    # Factory class methods to create specific Toolkit icons
    ##########################################################################################################
    # TODO add a classmethod to create all icons used in Toolkit
    #

    @classmethod
    def ValidationOk(cls, size=MEDIUM):
        icon = cls.resource_path("validation_ok", size)
        return cls(icon)

    @classmethod
    def ValidationWarning(cls, size=MEDIUM):
        icon = cls.resource_path("validation_warning", size)
        return cls(icon)

    @classmethod
    def ValidationError(cls, size=MEDIUM):
        icon = cls.resource_path("validation_error", size)
        return cls(icon)

    @classmethod
    def RedRefresh(cls, size=MEDIUM):
        icon = cls.resource_path("refresh_red", size)
        return cls(icon)

    @classmethod
    def RedBullet(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("bullet_inactive", size),
            normal_on=cls.resource_path("bullet_active", size),
        )

    @classmethod
    def Lock(cls, size=MEDIUM):
        icon = cls.resource_path("lock", size)
        return cls(icon)

    @classmethod
    def GreenCheckMark(cls, size=MEDIUM):
        icon = cls.resource_path("check_mark_green", size)
        return cls(icon)

    @classmethod
    def RedCheckMark(cls, size=MEDIUM):
        icon = cls.resource_path("check_mark_red", size)
        return cls(icon)

    @classmethod
    def Filter(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("filter_inactive", size),
            normal_on=cls.resource_path("filter_active", size),
        )

    @classmethod
    def Info(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("info_inactive", size),
            normal_on=cls.resource_path("info_active", size),
        )

    @classmethod
    def TreeArrow(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("tree_arrow_expanded", size),
            normal_on=cls.resource_path("tree_arrow_collapsed", size),
        )

    @classmethod
    def ListViewMode(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("view_list_inactive", size),
            normal_on=cls.resource_path("view_list_active", size),
        )

    @classmethod
    def ThumbnailViewMode(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("view_thumbnail_inactive", size),
            normal_on=cls.resource_path("view_thumbnail_active", size),
        )

    @classmethod
    def GridViewMode(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("view_grid_inactive", size),
            normal_on=cls.resource_path("view_grid_active", size),
        )

    @classmethod
    def Toggle(cls, size=MEDIUM):
        return cls(
            normal_off=cls.resource_path("toggle_inactive", size),
            normal_on=cls.resource_path("toggle_active", size),
        )
