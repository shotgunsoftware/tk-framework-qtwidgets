# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


def check_project_search_supported(sg_connection):
    """
    A compatibility check to see if the current version of SG has the fix
    that allows text_search to be run for projects.

    :returns: ``True`` if project search is possible, ``False`` otherwise.


    .. warning::

        This method is not part of the public API. It will be removed without
        warning in the future.
    """

    server_caps = sg_connection.server_caps

    # make sure we're greater than or equal to SG v7.0.2
    return (
        hasattr(sg_connection, "server_caps") and
        server_caps.version and
        server_caps.version >= (7, 0, 2)
    )
