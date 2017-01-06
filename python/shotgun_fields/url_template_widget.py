# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from .label_base_widget import ElidedLabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta


class UrlTemplateWidget(ElidedLabelBaseWidget):
    """
    Display a ``url_template`` field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "url_template"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param str value: The url value to convert into a string
        """
        utils = self._bundle.import_module("utils")
        return utils.get_hyperlink_html(url=value, name=value)
