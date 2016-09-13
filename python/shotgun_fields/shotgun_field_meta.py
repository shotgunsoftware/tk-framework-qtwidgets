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
from sgtk.platform.qt import QtCore, QtGui
from .shotgun_field_manager import ShotgunFieldManager


# a list of class member names accumulated at import time. these names will be
# taken over by deriving classes as new instances are created.
TAKE_OVER_NAMES = []

def take_over(func):
    """
    Decorator to accumulate the names of members to take over in derived classes.

    :param func: A function or method to takeover in the derived class.
    """

    if hasattr(func, '__name__'):
        # regular method
        name = func.__name__
    elif hasattr(func, '__func__'):
        # static or class method
        name = func.__func__.__name__
    else:
        raise sgtk.TankError("Don't know how to take over member: %s" % (func,))
    TAKE_OVER_NAMES.append(name)
    return func


# use type to pull the metaclass for QWidget since Shiboken is not always directly available
# and it abstracts out any difference between PySide and PyQt
class ShotgunFieldMeta(type(QtGui.QWidget)):
    """
    The primary purpose of this class is to register widget classes with the
    :class:`shotgun_fields.ShotgunFieldManager`. Classes that specify this class
    as their ``__metaclass__``, and follow the protocols below, will be registered
    and available via the ``ShotgunFieldManager.create_widget()`` factory method.

    This class also provides default logic common to all Shotgun field widgets
    without requiring them to use multiple inheritance which can be tricky.

    The following protocols apply when using this class:

    - Classes defined with this metaclass must have the following:
        * A member named ``_DISPLAY_TYPE``, ``_EDITOR_TYPE``, or both. The value
          of these members should be a string matching the Shotgun field data
          type that the class will be responsible for displaying or editing.

    Example::

        class FloatDisplayWidget(QtGui.QLabel):
            __metaclass__ = ShotgunFieldMeta
            _DISPLAY_TYPE = "float"
            # ...

        class FloatEditorWidget(QtGui.QDoubleSpinBox):
            __metaclass__ = ShotgunFieldMeta
            _EDITOR_TYPE = "float"
            # ...

    The widgets shown above will be used by any SG field for the specified type.
    It is also possible to register widgets that are used only for specific
    fields on specific entities. To achieve this, use the ``_ENTITY_FIELDS``
    class member to define a list of tuples that explicitly defined the entity
    fields the widget should be used to display.

    Example::

        class SpecialFloatDisplayWidget(QtGui.QLabel):
            __metaclass__ = ShotgunFieldMeta
            _DISPLAY_TYPE = "float"
            _ENTITY_FIELDS = [
                ("CustomEntity07", "my_float_field"),
                ("CustomEntity11", "another_float_field"),
            ]
            # ...

    The widget defined above will only be used to display the fields in the
    ``_ENTITY_FIELDS`` list.

    - No class defined with this metaclass can define its own ``__init__`` method.
        * The metaclass defines an ``__init__`` that takes the arguments below
        * The class will pass all other keyword args through to the PySide widget
          constructor for the class' superclass.

    :param parent: Parent widget
    :type parent: :class:`PySide.QtGui.QWidget`
    :param entity: The Shotgun entity dictionary to pull the field value from.
    :type entity: Whatever is returned by the Shotgun API for this field
    :param str field_name: Shotgun field name
    :param bg_task_manager: The task manager the widget will use if it needs to run a task
    :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`

    - All instances of the class will have the following member variables set:
        * ``_entity``: The entity the widget is representing a field of (if passed in)
        * ``_field_name``: The name of the field the widget is representing
        * ``_bg_task_manager``: The task manager the widget should use (if passed in)
        * ``_bundle``: The current Toolkit bundle

    - All instances of this class can emit the following signals:
        * ``value_changed()``: Emitted when the value of the widget is changed
          either programmatically or via user interaction.

    - The following optional method can be defined by classes using this metaclass
        * ``setup_widget(self)``: called during construction after the superclass
          has been initialized and after the above member variables have been set.
        * ``set_value(self, value)``: called during construction after
          ``setup_widget`` returns. Responsible for setting the initial contents
          of the widget.
        * ``get_value()``: Returns the internal value stored for the widget. This
          value should match the format and type of data associated with the widget's
          field in Shotgun, as returned by the python API.

    - If ``set_value`` is not defined, then the class must implement the following methods:
        * ``_display_default(self)``: Set the widget to display its "blank" state
        * ``_display_value(self, value)``: Set the widget to display the value from Shotgun
        * These methods are called by the default implementation of ``set_value``.

    - Classes that handle display **and** editing of field values and must implement the following methods:
        * ``enable_editing(self, bool)``: Toggles the editability of the widget

    - Editor classes can optionally implement the following methods:
        * ``_begin_edit(self)``: Used to provide additional behavior/polish when
          when the user has requested to edit the field. An example would be automatically
          showing a combobox popup menu or selecting the text in a line edit.

    - Editor classes can optionally set the following members:
        * ``_IMMEDIATE_APPLY``: If True, it implies that interaction with the
          editor will apply a value. If False (default), it implies that the user
          must apply the value as a separate action (like clicking an apply button).
          This mainly provides a display hint to the :class:`.ShotgunFieldEditable` wrapper.

    """

    def __new__(mcl, name, parents, class_dict):
        # Construct the class object for a Shotgun field widget class
        # NOTE: not using docstring here. Can't seem to exclude it from sphinx
        # docs without eliminating the class docstring.

        # validate the class definition to make sure it implements the needed interface
        if ("_DISPLAY_TYPE" not in class_dict) and ("_EDITOR_TYPE" not in class_dict):
            raise ValueError("ShotgunFieldMeta classes must have a _DISPLAY_TYPE or _EDITOR_TYPE member variable")
        if "__init__" in class_dict:
            raise ValueError("ShotgunFieldMeta classes cannot define their own constructor")

        # take over class members if called out via the @take_over decorator
        for member_name in TAKE_OVER_NAMES:
            member = getattr(mcl, member_name, None)
            if member:
                mcl.take_over_if_not_defined(member_name, member, class_dict, parents)

        # register the signal that will be emitted as the value changes
        class_dict["value_changed"] = QtCore.Signal()

        # create the class instance itself
        field_class = super(ShotgunFieldMeta, mcl).__new__(mcl, name, parents, class_dict)

        # widgets can be used for multiple reasons (display, edit, editable, etc).
        # build a list of the different types for later registration.
        registration_types = []

        if "_DISPLAY_TYPE" in class_dict:
            field_type = class_dict["_DISPLAY_TYPE"]
            widget_type = ShotgunFieldManager.DISPLAY
            registration_types.append((field_type, widget_type))

        if "_EDITOR_TYPE" in class_dict:
            field_type = class_dict["_EDITOR_TYPE"]
            widget_type = ShotgunFieldManager.EDITOR
            registration_types.append((field_type, widget_type))

        if "_EDITABLE_TYPE" in class_dict:
            field_type = class_dict["_EDITABLE_TYPE"]
            widget_type = ShotgunFieldManager.EDITABLE
            registration_types.append((field_type, widget_type))

        # register all the types for this widget class
        for (field_type, widget_type) in registration_types:

            if "_ENTITY_FIELDS" in class_dict:
                # this is an override widget, meaning it is to be used for specific
                # entity+field combinations. Loop through those combinations and
                # register this class for each.
                for (entity_type, field_name) in class_dict["_ENTITY_FIELDS"]:
                    ShotgunFieldManager.register_entity_field_class(
                        entity_type, field_name, field_class, widget_type)
            else:
                # this widget is to be used for all fields of a certain type
                ShotgunFieldManager.register_class(field_type, field_class, widget_type)

        return field_class

    def __call__(cls, parent=None, entity_type=None, field_name=None, entity=None, bg_task_manager=None, delegate=False, **kwargs):
        """
        Create an instance of the given class.

        :param parent: Parent widget
        :type parent: :class:`~PySide.QtGui.QWidget`

        :param entity_type: Shotgun entity type
        :type field_name: String

        :param field_name: Shotgun field name
        :type field_name: String

        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field

        :param bg_task_manager: The task manager the widget will use if it needs to run a task
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`

        :param bool delegate: True if the widget field widget is being used as a delegate, False otherwise.

        Additionally pass all other keyword args through to the PySide widget constructor for the
        class' superclass.
        """
        # create the instance passing through just the QWidget compatible arguments
        instance = super(ShotgunFieldMeta, cls).__call__(parent=parent, **kwargs)

        # set the default member variables
        instance._value = None
        instance._entity = entity
        instance._entity_type = entity_type
        instance._field_name = field_name
        instance._bg_task_manager = bg_task_manager
        instance._bundle = sgtk.platform.current_bundle()
        instance._delegate = delegate

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
    @take_over
    def setup_widget(self):
        """
        Default method called to setup the widget.
        """
        return

    @staticmethod
    @take_over
    def set_value(self, value):
        """
        Set the value displayed by the widget.

        Calling this method will result in ``value_changed`` signal being emitted.

        :param value: The value displayed by the widget
        """
        self._value = value
        if value is None:
            self._display_default()
        else:
            self._display_value(value)
        self.value_changed.emit()

    @staticmethod
    @take_over
    def get_value(self):
        """
        :return: The internal value being displayed by the widget.
        """
        return self._value

    @staticmethod
    @take_over
    def get_entity(self):
        """
        :return: The entity associated with the field widget.
        """
        return self._entity

    @staticmethod
    @take_over
    def get_entity_type(self):
        """
        :return: The entity type associated with the field widget.
        """
        return self._entity_type

    @staticmethod
    @take_over
    def get_field_name(self):
        """
        :return: The field name associated with the field widget.
        """
        return self._field_name

    @staticmethod
    @take_over
    def _get_safe_str(self, value):
        """
        Returns a safe string representation of the supplied value.

        Handles unicode and QString values (PyQt).

        :param value: The value provided from the widget

        :return: A safe ``str`` representation of the value.
        """

        if isinstance(value, str):
            # it's a string anyway so just return
            return value

        if isinstance(value, unicode):
            # convert to utf-8
            return value.encode("utf8")

        if hasattr(QtCore, "QString"):
            # running PyQt!
            if isinstance(value, QtCore.QString):
                # QtCore.QString inherits from str but supports
                # unicode, go figure!  Lets play safe and return
                # a utf-8 string
                return str(value.toUtf8())

        # For everything else, just return as string
        return str(value)


