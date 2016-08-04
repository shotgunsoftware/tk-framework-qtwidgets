# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_model",
)

class SimpleTooltipModel(shotgun_model.SimpleShotgunModel):
    """
    A Shotgun model that sets simple tooltips for Shotgun entities.
    """
    def _set_tooltip(self, item, sg_item):
        """
        Sets the tooltip of the given item.

        :param item:    Shotgun model item that requires a tooltip.
        :param sg_item: Dictionary of the entity associated with the Shotgun
                        model item.
        """
        item.setToolTip(
            "%s: %s" % (
                sg_item.get("type", "Entity Type Unknown"),
                sg_item.get("code", "Entity Name Unknown"),
            )
        )
