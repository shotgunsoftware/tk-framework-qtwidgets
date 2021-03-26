# Copyright (c) 2021 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import sgtk
from sgtk import TankError
from sgtk.platform.qt import QtCore

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_model"
)


class ViewItemRolesMixin(object):
    """
    A mixin class that may be used with any subclass of QAbstractItemModel, and the model data is
    displayed using the :class:`ViewItemDelegate`.

    This class will add item data roles to the model class, which may be used by the
    :class:`ViewItemDelegate`. This class also provides convenience methods to set a method for
    any role, which will then be called to retrieve the item data for that role.
    """

    @classmethod
    def initialize_roles(cls, next_available_role=QtCore.Qt.UserRole, reset=False):
        """
        Initialize the item data roles. This should only be called once.

        :param next_available_role: The next available custom role to use.
        :type next_available_role: long

        :return: The updated next available role for the model. This is the given next available
                 role plus the number of new role added to the model class.
        :rtype: long
        """

        if cls.initialized_roles() and not reset:
            # Already intiialized for this class.
            return next_available_role

        # Update this when new roles added below.
        num_roles = 11
        (
            cls.VIEW_ITEM_THUMBNAIL_ROLE,  # Thumbnail data
            cls.VIEW_ITEM_HEADER_ROLE,  # Title string
            cls.VIEW_ITEM_SUBTITLE_ROLE,  # Subtitle string
            cls.VIEW_ITEM_TEXT_ROLE,  # Longer details string
            cls.VIEW_ITEM_SHORT_TEXT_ROLE,  # Condensed text string for smaller items
            cls.VIEW_ITEM_ICON_ROLE,  # Icon data
            cls.VIEW_ITEM_EXPAND_ROLE,  # Item row expand state flag
            cls.VIEW_ITEM_WIDTH_ROLE,  # Item width int
            cls.VIEW_ITEM_HEIGHT_ROLE,  # Item height int
            cls.VIEW_ITEM_LOADING_ROLE,  # Item loading state flag
            cls.VIEW_ITEM_SEPARATOR_ROLE,  # Item has separator flag
        ) = range(next_available_role, next_available_role + num_roles)

        # Mark this class as initialized
        cls._initialized_roles = True

        # Return the next available role now that additional roles have been added to the model class.
        return next_available_role + num_roles

    @classmethod
    def initialized_roles(cls):
        """
        Returns True if the roles have been initialized for this class.
        """

        return hasattr(cls, "_initialized_roles") and cls._initialized_roles

    @property
    def role_methods(self):
        """
        Get or set the dictionary mapping between :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole` and
        the method to be used to retrieve the item data for the role.
        """

        if not hasattr(self, "_role_methods"):
            self._role_methods = {}

        return self._role_methods

    @role_methods.setter
    def role_methods(self, value):
        self._role_methods = value

    def get_method_for_role(self, role):
        """
        Return the hook method that should be called to retrieve the data for the model role.

        :param role: The :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole` role.
        :return: A callable hook method if one has been defined for this role, else None.
        """

        return self.role_methods.get(role)

    def set_data_for_role_methods(self, item, data=None):
        """
        For each role and method key-value pair defined by `role_methods`, set the item data for
        the role to return the associated method. This method can then be invoked to retreieve the
        data for the item's role.

        :param item: The item to set the data for.
        :type item: :class:`sgtk.platform.qt.QtGui.QStandardItem`
        :param data: Optional data to pass to the role's method.
        :type data: dict
        :return: None
        """

        args = [data] if data else []

        for role in self._role_methods:
            item.setData(
                lambda r=role, i=item, a=args: self._execute_data_role_method(r, i, *a),
                role,
            )

    def _execute_data_role_method(self, role, item, *args, **kwargs):
        """
        This method will execute the method defined for the given role and item.

        :param role: The role to lookup the method to execute.
        :type role: :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`
        :param item: The item to execute the method for.
        :type item: :class:`sgkt.platform.qt.QtGui.QStandardItem`
        :param args: Positional arguments to pass to the method to execute.
        :type args: list
        :param kwargs: Keyword arguments to pass to the method to execute.
        :type kwargs: dict
        :return: The sanitized value returned by the role's method.
        """

        result = None
        data_method = self._role_methods.get(role)

        # Append any extra arguments that need to be collected at dynamically at this point in time.
        (extra_args, extra_kwargs) = self._get_args_for_role_method(item, role)
        args += extra_args
        kwargs.update(extra_kwargs)

        if data_method:
            try:
                result = data_method(item, *args, **kwargs)
            except TypeError as error:
                raise TankError(
                    "Failed to execute the method defined to retrieve item data for role `{role}`.\nError: {msg}".format(
                        role=role, msg=error
                    )
                )

        # Santize the result before returning
        return shotgun_model.util.sanitize_qt(result)

    def _get_args_for_role_method(self, item, role):
        """
        This method will be called before executing the method to retrieve the item
        data for a given role.

        Override this method to return any additional positional or keyword arguments to
        pass along to the method executed for a role.staticmethod

        :param item: The model item.
        :type item: :class:`sgtk.platform.qt.QtGui.QStandardItem`
        :param role: The item role.
        :type role: :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole`

        :return: Positional or keyword arguments to pass to a method executed to retreive
                 item data for a role.
        :rtype: tuple(list, dict)
        """

        return ((), {})
