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

def get_hyperlink_html(url, name):
    """
    Provides an html string for a hyperlink pointing to the given URL
    and displaying the provided string name.

    :param str url: The URL that the hyperlink navigates to.
    :param str name: The string name to display.

    :return: HTML string.
    """
    # Older versions of core don't have the SG_LINK_COLOR constant, so we'll
    # just fall back on SG_FOREGROUND_COLOR in that case.
    color = sgtk.platform.constants.SG_STYLESHEET_CONSTANTS.get(
        "SG_LINK_COLOR",
        sgtk.platform.constants.SG_STYLESHEET_CONSTANTS["SG_FOREGROUND_COLOR"]
    )

    html = "<a href='%s' style='text-decoration: none; color: %s'><b>%s</b></a>" % (
        url,
        color,
        name,
    )

    return html
