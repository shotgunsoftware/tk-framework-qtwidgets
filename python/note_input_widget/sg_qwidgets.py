# Copyright (c) 2024 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import sgtk

sg_qwidgets = sgtk.platform.current_bundle().import_module("sg_qwidgets")
SGSubmitPushButton = sg_qwidgets.SGSubmitPushButton
SGCancelPushButton = sg_qwidgets.SGCancelPushButton