# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .shotgun_field_factory import ShotgunFieldFactory
from .entity_widget import EntityWidget


class MultiEntityWidget(EntityWidget):
    def __init__(self, parent=None, value=None):
        EntityWidget.__init__(self, parent)

        if value is not None:
            self.setText(", ".join([self._entity_dict_to_html(entity) for entity in value]))


ShotgunFieldFactory.register("multi_entity", MultiEntityWidget)
