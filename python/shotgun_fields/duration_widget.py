# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta
from tank_vendor import six


@six.add_metaclass(ShotgunFieldMeta)
class DurationWidget(LabelBaseWidget):
    """
    Display a ``duration`` field value as returned by the Shotgun API.
    """

    _DISPLAY_TYPE = "duration"
