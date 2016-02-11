# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Widget that represents the value of a timecode field in Shotgun
"""
from .shotgun_field_manager import ShotgunFieldManager
from .label_base_widget import LabelBaseWidget


class TimecodeWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a timecode field value as returned by the Shotgun API.
    """

    pass

ShotgunFieldManager.register("timecode", TimecodeWidget)
