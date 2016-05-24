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
from .shotgun_field_delegate import ShotgunFieldDelegate
from .shotgun_field_editable import ShotgunFieldEditable, ShotgunFieldNotEditable

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class ShotgunFieldManager(QtCore.QObject):
    """
    Inherited from a :class:`~PySide.QtCore.QObject`, this class acts as a factory
    for the set of widgets that can display values from Shotgun in a way appropriate
    to their field type.

    :signals:
        ``initialized()`` - Fires when the manager has finished running all the background tasks
        it needs for its functionality

    :enum: ``DISPLAY, EDITOR, EDITABLE`` - Enumeration for widget types managed and
        provided by the class
    """

    # dictionary that keeps the mapping from Shotgun data type to widget class
    __WIDGET_TYPE_CLS_MAP = {}

    # fires when we are ready to manage the widgets
    initialized = QtCore.Signal()

    # widget types enumeration
    _WIDGET_TYPES = (DISPLAY, EDITOR, EDITABLE) = ("display", "editor", "editable")

    ############################################################################
    # class methods

    @classmethod
    def get_class(cls, sg_entity_type, field_name, widget_type=DISPLAY):
        """
        Returns the registered class associated with the field name for the
        supplied entity and widget type.

        ``widget_type`` must be one of the enum values ``DISPLAY``, ``EDITOR``, or
        ``EDITABLE`` defined by the manager class. The default is ``DISPLAY``.

        This method typically doens't need to be called. Use the :meth:`.create_widget`
        to get an instance of a registered class.

        :param str sg_entity_type: Shotgun entity type
        :param str field_name: Shotgun field name
        :param str widget_type: The type of widget class to return

        :returns: :class:`~PySide.QtGui.QWidget` class or ``None`` if the field
            type has no display widget

        :raises: :class:`ValueError` if the supplied ``widget_type`` is not known.
        """
        if widget_type not in cls._WIDGET_TYPES:
            raise ValueError(
                "ShotgunFieldManager unable to retrieve fields of type: %s " %
                (widget_type,)
            )

        data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)
        return cls.__WIDGET_TYPE_CLS_MAP.get(data_type, {}).get(widget_type)

    @classmethod
    def register_class(cls, field_type, widget_class, widget_type):
        """
        Register a widget class for the given Shotgun field type.

        ``widget_type`` must be one of the enum values ``DISPLAY``, ``EDITOR``, or
        ``EDITABLE`` defined by the manager class.

        This method typically does not need to be called. Widget classes are
        typically registered as they are imported (when using the
        :class:`.ShotgunFieldMeta` class).

        :param str field_type: The data type of the field to associate with a type of widget
        :param widget_class: The display widget class to associate with the given field type
        :type widget_class: :class:`PySide.QtGui.QWidget`
        :param str widget_type: The type of widget class to register.

        :raises: :class:`ValueError` if the supplied ``widget_type`` is not known.
        """

        if widget_type not in cls._WIDGET_TYPES:
            raise ValueError(
                "ShotgunFieldManager unable to register fields of type: %s " %
                (widget_type,)
            )

        # TODO: consider removing this restriction if we want to allow developers
        # to override the default registered widget classes
        if widget_type in cls.__WIDGET_TYPE_CLS_MAP.get(field_type, {}):
            raise ValueError(
                "%s widget for field_type %s already registered" %
                (widget_type, field_type)
            )

        cls.__WIDGET_TYPE_CLS_MAP.setdefault(field_type, {})[widget_type] = widget_class

    ############################################################################
    # special methods

    def __init__(self, parent, bg_task_manager=None):
        """
        Initialize the field manager factory.

        :param parent: Parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        :param bg_task_manager: Optional Task manager.  If this is not passed in one will be created
                when the object is initialized.
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        QtCore.QObject.__init__(self, parent)

        self._task_manager = bg_task_manager
        self._initialized = False

    def __del__(self):
        """
        Destructor.

        Unregisters the field manager's background task manager.
        """
        if self._initialized:
            shotgun_globals.unregister_bg_task_manager(self._task_manager)

    ############################################################################
    # public methods

    def create_delegate(self, sg_entity_type, field_name, view):
        """
        Returns a delegate that can be used in the given view to show data from the given
        field from the given entity type.  This delegate is designed to be used by items
        from a shotgun_model's additional columns.  It assumes that the value for the field
        will be stored in the ``SG_ASSOCIATED_FIELD_ROLE``
        (via the :class:`~tk-framework-shotgunutils:shotgun_model.ShotgunModel`) role of
        its current index.

        :param str sg_entity_type: Shotgun entity type

        :param str field_name: Shotgun field name

        :param view: The parent view for this delegate
        :type view:  :class:`~PySide.QtGui.QWidget`

        :returns: A :class:`ShotgunFieldDelegate` configured to represent the given field
        """
        display_class = self.get_class(sg_entity_type, field_name)
        editor_class = self.get_class(sg_entity_type, field_name, self.EDITOR)
        return ShotgunFieldDelegate(
            sg_entity_type,
            field_name,
            display_class,
            editor_class,
            view,
            bg_task_manager=self._task_manager
        )

    def create_label(self, sg_entity_type, field_name):
        """
        Returns a widget that can be used as a label for the given field.

        :param str sg_entity_type: Shotgun entity type
        :param str field_name: Shotgun field name

        :returns: :class:`~PySide.QtGui.QLabel`
        """
        display_name = shotgun_globals.get_field_display_name(sg_entity_type, field_name)
        return QtGui.QLabel(display_name)

    def create_widget(self, sg_entity_type, field_name, widget_type=EDITABLE, entity=None, parent=None, **kwargs):
        """
        Returns a widget associated with the entity and field type if a
        corresponding widget class been registered.

        ``widget_type`` must be one of the enum values ``DISPLAY``, ``EDITOR``, or
        ``EDITABLE`` defined by the manager class.

        If the entity is passed in and has the value for the requested field
        then the initial contents of the widget will display that value.

        Any keyword args other than those below will be passed to the
        constructor of whatever ``QWidget`` the field widget wraps.

        :param str sg_entity_type: Shotgun entity type
        :param str field_name: Shotgun field name
        :param str widget_type: The type of widget to return.
        :param dict entity: The Shotgun entity dictionary to pull the field value from.
        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :returns: :class:`~PySide.QtGui.QWidget` or ``None`` if the field type has no display widget
        """

        if widget_type is self.EDITABLE:
            widget = self._create_editable_widget(
                sg_entity_type, field_name, entity, parent, **kwargs)
        elif widget_type is self.EDITOR:
            widget = self._create_editor_widget(
                sg_entity_type, field_name, entity, parent, **kwargs)
        elif widget_type is self.DISPLAY:
            widget = self._create_display_widget(
                sg_entity_type, field_name, entity, parent, **kwargs)
        else:
            raise TypeError(
                "Unknown widget type supplied to ShotgunFieldManager."
                "create_widget: %s" % (widget_type,)
            )

        return widget

    def initialize(self):
        """
        Initialize the task manager.

        When initialization is complete the initialized signal will be emitted.
        """
        if self._initialized:
            # already initialized
            return

        if self._task_manager is None:
            # create our own task manager if one wasn't passed in
            task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")
            self._task_manager = task_manager.BackgroundTaskManager(
                parent=self,
                max_threads=1,
                start_processing=True
            )

        # let shotgun globals start loading the schema
        shotgun_globals.register_bg_task_manager(self._task_manager)
        shotgun_globals.run_on_schema_loaded(self.__schema_loaded)
        self._initialized = True

    def supported_fields(self, sg_entity_type, field_names, widget_type=None):
        """
        Returns the subset of fields from field_names that have an associated widget class.
        Field_names may be in "bubbled" notation, for example "sg_task.Task.assignee".

        ``widget_type`` must be one of the enum values ``DISPLAY``, ``EDITOR``, or
        ``EDITABLE`` defined by the manager class or ``None``.

        The default is to return a list of field names that have an associated
        widget of any type registered. If the ``widget_type`` parameter is
        supplied, then the returned fields will be limited to fields for which the
        manager can generate widgets of that type.


        :param str sg_entity_type: Shotgun entity type
        :param list field_names: An list of (:obj:`str`) Shotgun field names
        :param str widget_type: The type of widget class to check for support.

        :returns: The subset of field_names that have associated widget classes.
        """
        supported_fields = []

        # build a list of all the fields whose type is in the field map
        for field_name in field_names:
            # handle bubbled field syntax
            if "." in field_name:
                (field_entity_type, short_name) = field_name.split(".")[-2:]
            else:
                (field_entity_type, short_name) = (sg_entity_type, field_name)
            data_type = shotgun_globals.get_data_type(field_entity_type, short_name)
            if data_type in self.__WIDGET_TYPE_CLS_MAP:
                if widget_type:
                    # caller wants to know if which fields are supported for
                    # a given type (display, editor, editable)
                    display_cls = self.get_class(
                        sg_entity_type, field_name, widget_type=self.DISPLAY)
                    editor_cls = self.get_class(
                        sg_entity_type, field_name, widget_type=self.EDITOR)
                    editable_cls = self.get_class(
                        sg_entity_type, field_name, widget_type=self.EDITABLE)

                    if widget_type == self.DISPLAY and display_cls:
                        supported_fields.append(field_name)
                    elif widget_type == self.EDITOR and editor_cls:
                        supported_fields.append(field_name)
                    elif widget_type == self.EDITABLE:
                        # if editable class registered, supported. if we have
                        # both a display and editor clas, then supported.
                        if editable_cls:
                            supported_fields.append(field_name)
                        elif display_cls and editor_cls:
                            supported_fields.append(field_name)
                else:
                    # only wants to know if some widget is registered
                    supported_fields.append(field_name)

        return supported_fields

    ############################################################################
    # protected methods

    def _create_display_widget(self, sg_entity_type, field_name, entity=None, parent=None, **kwargs):
        """
        Returns an instance of the display widget registered for the supplied field type.

        If the entity is passed in and has the value for the requested field in it then the
        initial contents of the widget will display that value.

        Any keyword args other than those below will be passed to the constructor of whatever
        ``QWidget`` the field widget wraps.

        :param str sg_entity_type: Shotgun entity type
        :param str field_name: Shotgun field name
        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field
        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :returns: :class:`~PySide.QtGui.QWidget` or ``None`` if the field type has no display widget
        """
        display_cls = self.get_class(sg_entity_type, field_name)
        widget = None

        if display_cls:
            # instantiate the widget
            widget = display_cls(
                parent=parent,
                entity_type=sg_entity_type,
                field_name=field_name,
                entity=entity,
                bg_task_manager=self._task_manager,
                **kwargs
            )

            # registered classes can act as both display and editor. check to
            # see if the classes match, and if so, disable editing since only
            # display was requested.
            editor_cls = self.get_class(sg_entity_type, field_name, self.EDITOR)
            if editor_cls == display_cls:
                widget.enable_editing(False)

        return widget

    def _create_editor_widget(self, sg_entity_type, field_name, entity=None, parent=None, **kwargs):
        """
        Returns an instance of the editor widget registered for the supplied field type.

        If the entity is passed in and has the value for the requested field in it then the
        initial contents of the widget will edit that value.

        Any keyword args other than those below will be passed to the constructor of whatever
        ``QWidget`` the field widget wraps.

        :param str sg_entity_type: Shotgun entity type
        :param str field_name: Shotgun field name
        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field
        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :returns: :class:`~PySide.QtGui.QWidget` or ``None`` if the field type has no editor widget
        """

        # check to make sure the field is editable. if it is not, return a
        # wrapped version of the display widget that indicates that the field
        # is not editable.
        if not shotgun_globals.field_is_editable(sg_entity_type, field_name):
            display_widget = self._create_display_widget(
                sg_entity_type, field_name, entity, parent, **kwargs)
            if display_widget:
                return ShotgunFieldNotEditable(display_widget)
            else:
                # no guarantee that a display widget has been registered
                return None

        # the field is editable, try to get the editor class
        editor_cls = self.get_class(sg_entity_type, field_name, self.EDITOR)
        widget = None

        if editor_cls:
            # instantiate the widget
            widget = editor_cls(
                parent=parent,
                entity_type=sg_entity_type,
                field_name=field_name,
                entity=entity,
                bg_task_manager=self._task_manager,
                **kwargs
            )

            # registered classes can act as both display and editor. check to
            # see if the classes match, and if so, make sure the editor is enabled
            display_cls = self.get_class(sg_entity_type, field_name)
            if display_cls == editor_cls:
                # display and edit classes are the same. we need to make sure
                # we enable the editing
                widget.enable_editing(True)

        return widget

    def _create_editable_widget(self, sg_entity_type, field_name, entity=None, parent=None, **kwargs):
        """
        Returns an instance of the editable widget registered for the supplied field type.

        If no editable widget is registered, a wrapped widget will be constructed
        using the registered display and editor widgets.

        If the entity is passed in and has the value for the requested field in it then the
        initial contents of the widget will edit that value.

        Any keyword args other than those below will be passed to the constructor of whatever
        ``QWidget`` the field widget wraps.

        :param str sg_entity_type: Shotgun entity type
        :param str field_name: Shotgun field name
        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field
        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :returns: :class:`~PySide.QtGui.QWidget` or ``None`` if the field type
            has no editable widget and one could not be constructed.
        """

        editable_cls = self.get_class(sg_entity_type, field_name, self.EDITABLE)
        if editable_cls:
            # instantiate the widget
            widget = editable_cls(
                parent=parent,
                entity_type=sg_entity_type,
                field_name=field_name,
                entity=entity,
                bg_task_manager=self._task_manager,
                **kwargs
            )
            return widget

        # no registered editable widget. that's ok, we'll try to construct one
        # with the registered display/editor classes using `ShotgunEditableWidget`
        # as a wrapper (stacked widget)
        display_cls = self.get_class(sg_entity_type, field_name)

        if not display_cls:
            # nothing to do if can't even display the field
            return None

        display_widget = self._create_display_widget(
            sg_entity_type, field_name, entity, parent, **kwargs)

        # check to make sure the field is editable. if it is not, return a
        # wrapped version of the display widget that indicates that the field
        # is not editable.
        if not shotgun_globals.field_is_editable(sg_entity_type, field_name):
            return ShotgunFieldNotEditable(display_widget)

        editor_cls = self.get_class(sg_entity_type, field_name, self.EDITOR)
        if editor_cls and editor_cls == display_cls:
            # if the editor and display are the same, just return the editing
            # enabled version of the display widget.
            display_widget.enable_editing(True)
            return display_widget

        if not editor_cls:
            return ShotgunFieldNotEditable(display_widget)

        editor_widget = self._create_editor_widget(
            sg_entity_type, field_name, entity, parent, **kwargs)

        # should have both a display and eidtor widget, wrap them up and return
        return ShotgunFieldEditable(display_widget, editor_widget, parent)

    ############################################################################
    # private methods

    def __schema_loaded(self):
        """
        Internal method that will be called when the schema is available.
        """
        self.initialized.emit()


# import the actual field types to give them a chance to register
from . import (
    checkbox_widget,
    currency_widget,
    date_and_time_widget,
    date_widget,
    entity_widget,
    file_link_widget,
    float_widget,
    footage_widget,
    image_widget,
    list_widget,
    multi_entity_widget,
    number_widget,
    percent_widget,
    status_list_widget,
    tags_widget,
    text_widget,
    url_template_widget,
)

# TODO: wait to register timecode field until the fps associated with this field
#  is available from the API
# from . import timecode_widget

# TODO: wait to register duration field until display options for hours versus
# days and of hours in a day are available to the API
# from . import duration_widget
