# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .shotgun_field_manager import ShotgunFieldManager
from .entity_widget import EntityWidget


class MultiEntityWidget(EntityWidget):
    def __init__(self, parent=None, value=None, bg_task_manager=None, **kwargs):
        EntityWidget.__init__(self, parent, **kwargs)
        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.clear()
        else:
            self.setText(", ".join([self._entity_dict_to_html(entity) for entity in value]))

ShotgunFieldManager.register("multi_entity", MultiEntityWidget)
