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
from .label_base_widget import LabelBaseWidget


class DurationWidget(LabelBaseWidget):
    pass

# wait to register duration field until display options for hours versus days
# and # of hours in a day are available to the API
# ShotgunFieldManager.register("duration", DurationWidget)
