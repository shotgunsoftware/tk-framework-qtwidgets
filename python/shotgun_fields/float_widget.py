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
Widget that represents the value of a float field in Shotgun
"""
import locale
from .label_base_widget import LabelBaseWidget
from .widget_metaclass import ShotgunFieldMeta


class FloatWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a float field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _FIELD_TYPE = "float"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: Float
        """
        return locale.format("%.2f", value, grouping=True)
