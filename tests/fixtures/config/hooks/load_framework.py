# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Pick environment hook.
"""

from tank import get_hook_baseclass


class LoadFramework(get_hook_baseclass()):
    """
    Picks the environment based on the context.
    """

    def load_widgets_framework(self, name):
        """
        Always picks the test environment unless step is not set, in which case
        it picks the entity environment.
        """
        return self.load_framework(name)
