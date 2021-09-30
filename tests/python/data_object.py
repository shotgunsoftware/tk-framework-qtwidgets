# Copyright (c) 2021 Autoiesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.


class _TestDataObject(object):
    """
    Class used for generating test data objects.
    """

    def __init__(self, property_1, property_2, property_3):
        """
        Constructor. Initialize the object properties.
        """

        self._property_1 = property_1
        self._property_2 = property_2
        self._property_3 = property_3

    @property
    def property_1(self):
        return self._property_1

    @property
    def property_2(self):
        return self._property_2

    @property
    def property_3(self):
        return self._property_3
