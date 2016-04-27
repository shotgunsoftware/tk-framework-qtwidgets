# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
This module implements a central place to deal with the set of widgets that
represent the different types of Shotgun fields.

An example of how this functionality can be used to populate a QTableWidget
with the results of a given Shotgun query is:

    class ExampleTableWidget(QtGui.QWidget):
        def __init__(self):
            QtGui.QWidget.__init__(self)

            # grab the current app bundle for use later
            self._app = sgtk.platform.current_bundle()

            # initialize the field manager
            self._fields_manager = shotgun_fields.ShotgunFieldManager(self)
            self._fields_manager.initialized.connect(self.populate_dialog)
            self._fields_manager.initialize()

        def populate_dialog(self):
            entity_type = "Version"
            entity_query = []

            # grab all of the fields on the entity type
            fields = sorted(self._app.shotgun.schema_field_read(entity_type).keys())

            # query Shotgun for the entities to display
            entities = self._app.shotgun.find(entity_type, entity_query, fields=fields)

            # set the headers for each field
            field_labels = []
            for field in fields:
                field_labels.append(shotgun_globals.get_field_display_name(entity_type, field))

            # create the table that will display all the data
            table = QtGui.QTableWidget(len(entities), len(fields), self)
            table.setHorizontalHeaderLabels(field_labels)

            # populate the table with the data in the entities returned by the query above
            for (i, entity) in enumerate(entities):
                for (j, field) in enumerate(fields):
                    # create the widget for each field
                    widget = self._fields_manager.create_display_widget(entity_type, field, entity)
                    if widget is None:
                        # backup in case the manager does not understand this field type
                        widget = QtGui.QLabel("No widget")

                    # put the widget into the table
                    table.setCellWidget(i, j, widget)

            # update widths and setup the table to be displayed
            table.resizeColumnsToContents()
            layout = QtGui.QVBoxLayout(self)
            layout.addWidget(table)
            self.setLayout(layout)

Or when using this functionality to display data from a ShotgunModel in a table view:

class ExampleTableView(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        # grab a field manager to get the delegate
        self.fields_manager = shotgun_fields.ShotgunFieldManager(self)
        self.fields_manager.initialized.connect(self.on_initialized)
        self.fields_manager.initialize()

    def on_initialized(self):
        entity_type = "Version"

        # grab all displayable fields on the entity type, with "code" first
        fields = shotgun_globals.get_entity_fields(entity_type)
        fields = self.fields_manager.supported_fields(entity_type, fields)
        fields = ["code"] + [f for f in fields if f != "code"]

        # setup the model and view
        self.model = shotgun_model.SimpleShotgunModel(self)
        self.model.load_data(entity_type, filters=[], fields=fields, columns=fields)
        self.table = views.ShotgunTableView(self.fields_manager, parent=self)
        self.table.setModel(self.model)

        # and layout the dialog
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.table)
        self.setLayout(layout)
"""
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .shotgun_field_delegate import ShotgunFieldDelegate
from .shotgun_field_editable import ShotgunFieldEditable

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class ShotgunFieldManager(QtCore.QObject):
    """
    Inherited from a :class:`~PySide.QtCore.QObject`, this class acts as a factory
    for the set of widgets that can display values from Shotgun in a way appropriate
    to their field type.

    :signal initialized(): Fires when the manager has finished running all the background tasks
        it needs for its functionality
    """

    # dictionary that keeps the mapping from Shotgun data type to widget class
    __DISPLAY_TYPE_MAP = {}

    # first when we are ready to manage the widgets
    initialized = QtCore.Signal()

    @classmethod
    def register_display(cls, field_type, widget_class):
        """
        Register the display widget class that will be used for the given Shotgun field type.

        :param field_type: The data type of the field to associate with a type of widget
        :type field_type: String

        :param widget_class: The display widget class to associate with the given field type
        :type widget_class: :class:`PySide.QtGui.QWidget`
        """
        if "display" in cls.__DISPLAY_TYPE_MAP.get(field_type, {}):
            raise ValueError("display widget for field_type %s is already registered" % field_type)

        cls.__DISPLAY_TYPE_MAP.setdefault(field_type, {})["display"] = widget_class

    @classmethod
    def register_editor(cls, field_type, widget_class):
        """
        Register the editor widget class that will be used for the given Shotgun field type.

        :param field_type: The data type of the field to associate with a type of widget
        :type field_type: String

        :param widget_class: The display widget class to associate with the given field type
        :type widget_class: :class:`PySide.QtGui.QWidget`
        """
        if "editor" in cls.__DISPLAY_TYPE_MAP.get(field_type, {}):
            raise ValueError("editor widget for field_type %s is already registered" % field_type)

        cls.__DISPLAY_TYPE_MAP.setdefault(field_type, {})["editor"] = widget_class

    def __init__(self, parent, bg_task_manager=None):
        """
        Constructor.

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
        Destructor

        Unregister the task_manager
        """
        if self._initialized:
            shotgun_globals.unregister_bg_task_manager(self._task_manager)

    def initialize(self):
        """
        Initialize the task manager.  When initialization is complete the initialized signal
        will be emitted.
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

    def __schema_loaded(self):
        """
        Internal method that will be called when the schema is available.
        """
        self.initialized.emit()

    def supported_fields(self, sg_entity_type, field_names):
        """
        Returns the subset of fields from field_names that have an associated widget class.
        field_names may be in "bubbled" notation, for example "sg_task.Task.assignee".

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_names: An list of Shotgun field names
        :type field_names: List of Strings

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
            if data_type in self.__DISPLAY_TYPE_MAP:
                supported_fields.append(field_name)

        return supported_fields

    @classmethod
    def get_display_class(cls, sg_entity_type, field_name):
        """
        Returns the class of the display widget associated with the field type if it has been registered.

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_name: Shotgun field name
        :type field_name: String

        :returns: :class:`~PySide.QtGui.QWidget` class or None if the field type has no display widget
        """
        data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)
        return cls.__DISPLAY_TYPE_MAP.get(data_type, {}).get("display")

    def create_display_widget(self, sg_entity_type, field_name, entity=None, parent=None, **kwargs):
        """
        Returns an instance of the display widget associated with the field type if it has been registered.

        If the entity is passed in and has the value for the requested field in it then the
        initial contents of the widget will display that value.

        Any keyword args other than those below will be passed to the constructor of whatever
        QWidget the field widget wraps.

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_name: Shotgun field name
        :type field_name: String

        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :returns: :class:`~PySide.QtGui.QWidget` or None if the field type has no display widget
        """
        display_cls = self.get_display_class(sg_entity_type, field_name)

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

            editor_cls = self.get_editor_class(sg_entity_type, field_name)
            if editor_cls == display_cls:
                # this widget is editable by default. disable it.
                # XXX probably not best idea. need to be able to set it to read-only
                widget.setEnabled(False)

        return widget

    @classmethod
    def get_editor_class(cls, sg_entity_type, field_name):
        """
        Returns the class of the editor widget associated with the field type if it has been registered.

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_name: Shotgun field name
        :type field_name: String

        :returns: :class:`~PySide.QtGui.QWidget` class or None if the field type has no editor widget
        """
        data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)
        return cls.__DISPLAY_TYPE_MAP.get(data_type, {}).get("editor")

    def create_editor_widget(self, sg_entity_type, field_name, entity=None, parent=None, **kwargs):
        """
        Returns an instance of the editor widget associated with the field type if it has been registered.

        If the entity is passed in and has the value for the requested field in it then the
        initial contents of the widget will edit that value.

        Any keyword args other than those below will be passed to the constructor of whatever
        QWidget the field widget wraps.

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_name: Shotgun field name
        :type field_name: String

        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :returns: :class:`~PySide.QtGui.QWidget` or None if the field type has no editor widget
        """
        cls = self.get_editor_class(sg_entity_type, field_name)

        if cls:
            # instantiate the widget
            return cls(
                parent=parent,
                entity_type=sg_entity_type,
                field_name=field_name,
                entity=entity,
                bg_task_manager=self._task_manager,
                **kwargs
            )

        return None

    def create_editable_widget(self, sg_entity_type, field_name, entity=None, parent=None, **kwargs):
        """Returns a widget that shows the display widget, but can be edited."""
        # XXX docs

        display_cls = self.get_display_class(sg_entity_type, field_name)
        editor_cls = self.get_editor_class(sg_entity_type, field_name)

        # XXX tmp
        data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)

        if not display_cls:
            # XXX better error
            print "**** NO DISPLAY: " + data_type + " (" + field_name + ")"
            return None

        display_widget = self.create_display_widget(sg_entity_type, field_name, entity, parent, **kwargs)

        # XXX doc
        if editor_cls == display_cls:
            # if the editor and display are the same, just return the enabled
            # version of the display widget. currently this would only be the
            # checkbox widget. may need to revisit this logic for more
            # sophisticated widgets
            display_widget.setEnabled(True)
            return display_widget

        editor_widget = self.create_editor_widget(sg_entity_type, field_name, entity, parent, **kwargs)

        # XXX doc
        if not editor_widget:
            print "** NO EDITOR: " + data_type + " (" + field_name + ")"
            return display_widget

        #print "FOUND EDITOR: " + data_type + " (" + field_name + ")"
        return ShotgunFieldEditable(display_widget, editor_widget, parent)

    def create_delegate(self, sg_entity_type, field_name, view):
        """
        Returns a delegate that can be used in the given view to show data from the given
        field from the given entity type.  This delegate is designed to be used by items
        from a shotgun_model's additional columns.  It assumes that the value for the field
        will be stored in the ShotgunModel.SG_ASSOCIATED_FIELD_ROLE role of its current
        index.

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_name: Shotgun field name
        :type field_name: String

        :param view: The parent view for this delegate
        :type view:  :class:`~PySide.QtGui.QWidget`

        :returns: A :class:`ShotgunFieldDelegate` configured to represent the given field
        """
        display_class = self.get_display_class(sg_entity_type, field_name)
        editor_class = self.get_editor_class(sg_entity_type, field_name)
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

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_name: Shotgun field name
        :type field_name: String

        :returns: :class:`~PySide.QtGui.QLabel`
        """
        display_name = shotgun_globals.get_field_display_name(sg_entity_type, field_name)
        return QtGui.QLabel(display_name)

# import the actual field types to give them a chance to register
from . import (
    checkbox_widget, currency_widget, date_and_time_widget, date_widget, entity_widget,
    file_link_widget, float_widget, footage_widget, image_widget, list_widget, multi_entity_widget,
    number_widget, percent_widget, status_list_widget, tags_widget, text_widget, url_template_widget
)

# wait to register timecode field until the fps associated with this field
# is available from the API
# from . import timecode_widget

# wait to register duration field until display options for hours versus days
# and # of hours in a day are available to the API
# from . import duration_widget
