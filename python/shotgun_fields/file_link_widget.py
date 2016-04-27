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
Widget that represents the value of a url field in Shotgun
"""
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta


class FileLinkWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display a url field (also known as a file field) value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "url"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A dictionary as returned by the Shotgun API for a url field
        """
        str_val = value["name"]

        if value["link_type"] in ["web", "upload"]:
            str_val = "<a href='%s'>%s</a>" % (value["url"], str_val)
        elif value["link_type"] == "local":
            str_val = "<a href='file://%s'>%s</a>" % (value["local_path"], str_val)

        return str_val

    # XXX editor