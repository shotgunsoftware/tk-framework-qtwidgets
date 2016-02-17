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
from sgtk.platform.qt import QtGui
from .shotgun_field_manager import ShotgunFieldManager


# use type to pull the metaclass for QWidget since Shiboken is not always directly available
# and it abstracts out any difference between PySide and PyQt
class ShotgunFieldMeta(type(QtGui.QWidget)):
    """
    Metaclass to implement the default logic common to all Shotgun field widgets.
    This metaclass implements the following behaviors:

    - All classes defined with this metaclass must have a member named _FIELD_TYPE whose value is
      the string of the field data type that the class will be responsible for displaying.  The class
      will be registered with the field manager as the widget class for that data type.

    - No class defined with this metaclass can define its own __init__ method.  The metaclass defines
      an __init__ that takes the following arguments:

      :param parent: Parent widget
      :type parent: :class:`PySide.QtGui.QWidget`

      :param entity: The Shotgun entity dictionary to pull the field value from.
      :type entity: Whatever is returned by the Shotgun API for this field

      :param field_name: Shotgun field name
      :type field_name: String

      :param bg_task_manager: The task manager the widget will use if it needs to run a task
      :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`

      Additionally the class will pass all other keyword args through to the PySide widget
      constructor for the class' superclass.

    - All instances of the class will have the following member variables set:

      _entity: The entity the widget is representing a field of (if passed in)
      _field_name: The name of the field the widget is representing
      _bg_task_manager: The task manager the widget should use (if passed in)
      _bundle: The current Toolkit bundle

    - Optionally the class can define a method with the signature
        setup_widget(self)

      This method will be called during construction after the superclass has been
      initialized and after the above member variables have been set.

    - Optionally the class can define a method with the signature
        set_value(self, value)

      This method will be called during construction after setup_widget returns and
      is responsible for setting the initial contents of the widget.

    - If set_value is not defined, then the class must implement the following methods
        _display_default(self) - Set the widget to display its "blank" state
        _display_value(self, value) - Set the widget to display value

      These methods are called by the default implementation of set_value.
    """
    def __new__(mcl, name, parents, class_dict):
        """
        Construct the class object for a Shotgun field widget class
        """
        # validate the class definition to make sure it implements the needed interface
        if "_FIELD_TYPE" not in class_dict:
            raise ValueError("ShotgunFieldMeta classes must have a _FIELD_TYPE member variable")
        if "__init__" in class_dict:
            raise ValueError("ShotgunFieldMeta classes cannot define their own constructor")

        # take over interface methods if they have not already been defined
        mcl.take_over_if_not_defined("setup_widget", mcl.setup_widget, class_dict, parents)
        mcl.take_over_if_not_defined("set_value", mcl.set_value, class_dict, parents)

        # create the class instance itself
        field_class = super(ShotgunFieldMeta, mcl).__new__(mcl, name, parents, class_dict)

        # register the field type this class implements with the field manager
        ShotgunFieldManager.register(class_dict["_FIELD_TYPE"], field_class)

        return field_class

    def __call__(cls, parent=None, entity=None, field_name=None, bg_task_manager=None, **kwargs):
        """
        Create an instance of the given class.

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field

        :param field_name: Shotgun field name
        :type field_name: String

        :param bg_task_manager: The task manager the widget will use if it needs to run a task
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`

        Additionally pass all other keyword args through to the PySide widget constructor for the
        class' superclass.
        """
        # create the instance passing through just the QWidget compatible arguments
        instance = super(ShotgunFieldMeta, cls).__call__(parent=None, **kwargs)

        # set the default member variables
        instance._entity = entity
        instance._field_name = field_name
        instance._bg_task_manager = bg_task_manager
        instance._bundle = sgtk.platform.current_bundle()

        # do any widget setup that is needed
        instance.setup_widget()

        # then set the value
        instance.set_value(entity and entity.get(field_name) or None)

        return instance

    @classmethod
    def take_over_if_not_defined(mcl, method_name, method, class_dict, parents):
        """
        Method used during __new__ to add the given method to the class being
        created only if it hasn't been defined in the class or any of its parents.

        :param method_name: The name of the method to take over
        :type method_name: String

        :param method: The actual method to add to the class
        :type method: function

        :param class_dict: The class dictionary passed to __new__
        :type class_dict: dictionary

        :param parents: The ancestors of the class being created
        :type parents: List of classes
        """
        # first check if the method is directly defined
        if method_name in class_dict:
            return

        # then check each parent
        for parent in parents:
            if hasattr(parent, method_name):
                return

        # not defined anywhere, take it over
        class_dict[method_name] = method

    @staticmethod
    def setup_widget(self):
        """
        Default method called to setup the widget.
        """
        return

    @staticmethod
    def set_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value displayed by the widget
        """
        if value is None:
            self._display_default()
        else:
            self._display_value(value)
