# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtGui


class ShotgunTableView(QtGui.QTableView):
    """
    A subclass of :class:`~PySide.QtGui.QTableView` that will automatically set
    the column delegates to the appropriate delegate for the type of Shotgun data
    contained in them.
    """
    def __init__(self, fields_manager, parent=None):
        """
        Constructor

        :param fields_manager: The field manager to use when generating the delegates
        :type fields_manager: :class:`shotgun_fields.FieldsManager`

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        QtGui.QTableView.__init__(self, parent)
        self._fields_manager = fields_manager

        self.setMouseTracking(True)

        # identify the ways to initiate editing a field
        self.setEditTriggers(
            QtGui.QAbstractItemView.DoubleClicked |
            QtGui.QAbstractItemView.EditKeyPressed
        )

    def setModel(self, model):
        """
        Overrides the base class setModel.  This assumes that the model is a ShotgunModel
        and will set the delegates for each column to the appropriate delegate to display
        its Shotgun value.
        """
        QtGui.QTableView.setModel(self, model)

        # set the delegates
        columns_and_fields = model.get_additional_column_fields()
        for column_info in columns_and_fields:
            delegate = self._fields_manager.create_delegate(
                model.get_entity_type(), column_info["field"], self)
            self.setItemDelegateForColumn(column_info["column_idx"], delegate)
