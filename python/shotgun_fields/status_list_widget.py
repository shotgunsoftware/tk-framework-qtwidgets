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
Widget that represents the value of a status_list field in Shotgun
"""
import sgtk
from .label_base_widget import LabelBaseWidget
from .widget_metaclass import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class StatusListWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a status_list field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _FIELD_TYPE = "status_list"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: String that is a valid Shotgun status code
        """
        str_val = shotgun_globals.get_status_display_name(value)
        color_str = shotgun_globals.get_status_color(value)

        if color_str:
            # append colored box to indicate status color
            str_val = ("<span style='color: rgb(%s)'>&#9608;</span>&nbsp;%s" % (color_str, str_val))

        return str_val
