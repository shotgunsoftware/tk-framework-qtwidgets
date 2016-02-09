# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtGui
from .shotgun_field_factory import ShotgunFieldFactory


class UrlTemplateWidget(QtGui.QLabel):
    def __init__(self, parent=None, value=None):
        QtGui.QLabel.__init__(self, parent)

        if value is not None:
            self.setText("<a href='%s'>%s</a>" % (value, value))


ShotgunFieldFactory.register("url_template", UrlTemplateWidget)
