# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtGui
from .shotgun_field_factory import ShotgunFieldFactory

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class EntityWidget(QtGui.QLabel):
    def __init__(self, parent=None, value=None):
        QtGui.QLabel.__init__(self, parent)
        self.setOpenExternalLinks(True)

        self._bundle = sgtk.platform.current_bundle()

        if value is not None:
            self.setText(self._entity_dict_to_html(value))

    def _entity_dict_to_html(self, value):
        str_val = value["name"]
        entity_url = "%sdetail/%s/%d" % (self._bundle.sgtk.shotgun_url, value["type"], value["id"])
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(value["type"])
        str_val = "<a href='%s'><img align='absmiddle' src='%s'>%s</a>" % (entity_url, entity_icon_url, str_val)
        return str_val

ShotgunFieldFactory.register("entity", EntityWidget)
