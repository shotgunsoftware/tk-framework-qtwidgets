# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Wrapper for the various widgets used from frameworks so that they can be used
easily from with Qt Designer
"""

import sgtk

search_widget = sgtk.platform.current_bundle().import_module("search_widget")
SearchWidget = search_widget.SearchWidget

activity_stream = sgtk.platform.current_bundle().import_module("activity_stream")
ActivityStreamWidget = activity_stream.ActivityStreamWidget

from .shotgun_entities import ShotgunEntityCardWidget, ShotgunEntityCardDelegate

shotgun_fields = sgtk.platform.current_bundle().import_module("shotgun_fields")
ShotgunFieldManager = shotgun_fields.ShotgunFieldManager

shotgun_menus = sgtk.platform.current_bundle().import_module("shotgun_menus")
EntityFieldMenu = shotgun_menus.EntityFieldMenu
ShotgunMenu = shotgun_menus.ShotgunMenu

models = sgtk.platform.current_bundle().import_module("models")
ShotgunSortFilterProxyModel = models.ShotgunSortFilterProxyModel

from .simple_tooltip_model import SimpleTooltipModel
