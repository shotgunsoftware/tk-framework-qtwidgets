# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

def log_metric_group_media(bundle, action, properties=None):
    """
    Helper method for logging a media group metric

    :param bundle: A TankBundle reference to this application
    :param action: A str of a Media metric group action
    :param properties: A dict of metric properties to emit
    """

    try:
        from sgtk.util.metrics import EventMetric

        EventMetric.log(
            EventMetric.GROUP_MEDIA,
            action,
            properties=properties,
            bundle=bundle
        )
    except:
        # ignore all errors. ex: using a core that doesn't support metrics
        pass


def log_metric_created_note(bundle, source, entity_type):
    """
    Helper method for logging a "Created Note" note metric.

    :param bundle: A TankBundle reference to this application
    :param source: a str of the source e.g.: "Activity Stream", "Reply Note" etc.
    :param entity_type: a str representing an entity type such as Note, Project, Task etc.
    """

    fields = []  # # reserved for future use

    annotations = {}  # reserved for future use

    properties = {
        "Source": source,
        "Linked Entity Type": entity_type,
        "Field USed": fields,
        "Annotations": annotations
    }
    log_metric_group_media(
        bundle,
        "Created Note",
        properties
    )


def log_metric_created_reply(bundle, source):
    """
    Helper method for logging a "Created Reply" metric.

    :param bundle: A TankBundle reference to this application
    :param source: a str of the source e.g.: "Activity Stream", "Reply Note" etc.
    """

    properties = {
        "Source": source,
    }

    log_metric_group_media(
        bundle,
        "Created Reply",
        properties
    )
