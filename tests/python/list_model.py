# Copyright (c) 2021 Autoiesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.


import sgtk

try:
    from sgtk.platform.qt import QtCore
except:
    # components also use PySide, so make sure we have this loaded up correctly
    # before starting auto-doc.
    from tank.util.qt_importer import QtImporter

    importer = QtImporter()
    sgtk.platform.qt.QtCore = importer.QtCore
    sgtk.platform.qt.QtGui = importer.QtGui
    from sgtk.platform.qt import QtCore


class _TestListModel(QtCore.QAbstractListModel):
    """
    A subclass of the Qt QAbstractListModel. A very basic model to use for testing.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """

        super(_TestListModel, self).__init__(*args, **kwargs)

        self._data = []
        self._map_role_to_column = {QtCore.Qt.DisplayRole: 0}

    def set_internal_data(self, data):
        """
        Set the model's internal data.
        """

        self._data = data

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Override the base method.

        Returns the number of rows in the model.
        """

        if parent.isValid():
            return 0

        return len(self._data)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        Override the base method.

        Return the data for the index and role.
        """

        if not index.isValid():
            return None

        # Ensure the index is valid with the internal model data
        if index.row() < 0 or index.row() >= len(self._data):
            return None

        # Get the model data for this index
        row_value = self._data[index.row()]

        # Get the column associated with this role to index into the data for this row.
        column = self._map_role_to_column.get(role, -1)

        if column < 0 or column >= len(row_value):
            # Role not mapped to a column or invalid column
            return None

        return row_value[column]

    def map_role_to_column(self, role, column):
        """
        Map a column to a given role to extract data from an index.
        """

        self._map_role_to_column[role] = column
