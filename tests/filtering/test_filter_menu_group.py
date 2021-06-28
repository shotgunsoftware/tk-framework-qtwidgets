# Copyright (c) 2021 Autoiesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import os
import sys

import pytest

import sgtk

try:
    from sgtk.platform.qt import QtCore, QtGui
except:
    # components also use PySide, so make sure  we have this loaded up correctly
    # before starting auto-doc.
    from tank.util.qt_importer import QtImporter

    importer = QtImporter()
    sgtk.platform.qt.QtCore = importer.QtCore
    sgtk.platform.qt.QtGui = importer.QtGui


# Manually add the app modules to the path in order to import them here.
base_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "python")
)
filtering_dir = os.path.abspath(os.path.join(base_dir, "filtering"))
sys.path.extend([base_dir, filtering_dir])
from filter_item import FilterItem
from filter_menu_group import FilterMenuGroup


# TODO test
