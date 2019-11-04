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
Load framework hook.
"""

from tank import get_hook_baseclass


class LoadFramework(get_hook_baseclass()):
    def load_framework(self, name):
        """
        Loads the specified framework.

        This hook is necessary because we want to be able to load any framework we want,
        and frameworks can be loaded only from bundle's python folder and we don't have a
        full scale app.
        """
        return super(LoadFramework, self).load_framework(name)
