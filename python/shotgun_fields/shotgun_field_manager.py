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

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class ShotgunFieldManager(QtCore.QObject):
    __FIELD_TYPE_MAP = {}

    initialized = QtCore.Signal()

    @classmethod
    def register(cls, field_type, widget_class):
        """
        Register the widget class that will be used for the given Shotgun field type.

        :param field_type: The data type of the field to associate with a type of widget
        :param widget_class: The widget class to associate with the given field type
        :type widget_class: :class:`PySide.QtGui.QWidget`
        """
        if field_type in cls.__FIELD_TYPE_MAP:
            raise ValueError("field_type %s is already registered" % field_type)
        cls.__FIELD_TYPE_MAP[field_type] = widget_class

    def __init__(self, parent=None, bg_task_manager=None):
        """
        :param parent: Parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        :param bg_task_manager: Optional Task manager
        :class bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        QtCore.QObject.__init__(self, parent)

        self._task_manager = bg_task_manager
        self._initialized = False

    def __del__(self):
        if self._initialized:
            shotgun_globals.unregister_bg_task_manager(self._task_manager)

    def initialize(self):
        if self._task_manager is None:
            task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")
            self._task_manager = task_manager.BackgroundTaskManager(
                parent=self,
                max_threads=1,
                start_processing=True
            )

        shotgun_globals.register_bg_task_manager(self._task_manager)
        self._initialized = True
        shotgun_globals.run_on_schema_loaded(self.schema_loaded)

    def schema_loaded(self):
        self.initialized.emit()

    def supported_fields(self, sg_entity_type, field_names):
        """
        Returns the subset of fields from field_names that have an associated widget class.

        :param sg_entity_type: Shotgun entity type
        :param field_names: An array of Shotgun field names
        :returns: The subset of the field_names array that has associated widget classes.
        """
        supported_fields = []
        for field_name in field_names:
            data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)
            if data_type in self.__FIELD_TYPE_MAP:
                supported_fields.append(field_name)
        return supported_fields

    def create_widget(self, sg_entity_type, field_name, value=None, parent=None, **kwargs):
        """
        Returns the widget class associated with the field type if it has been registered.

        :param sg_entity_type: Shotgun entity type
        :param field_name: Shotgun field name
        :returns: :class:`~PySide.QtGui.QWidget` or None if not found
        """
        data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)
        if data_type in self.__FIELD_TYPE_MAP:
            cls = self.__FIELD_TYPE_MAP[data_type]
            return cls(
                parent=parent,
                value=value,
                bg_task_manager=self._task_manager,
                **kwargs
            )
        return None

    def create_label(self, sg_entity_type, field_name):
        """
        Returns a widget that can be used as a label for the given field.

        :param sg_entity_type: Shotgun entity type
        :param field_name: Shotgun field name
        :returns: :class:`~PySide.QtGui.QWidget` or None if not found
        """
        display_name = shotgun_globals.get_field_display_name(sg_entity_type, field_name)
        return QtGui.QLabel(display_name)


# import the actual field types to give them a chance to register
from . import checkbox_widget
from . import currency_widget
from . import date_and_time_widget
from . import date_widget
from . import duration_widget
from . import entity_widget
from . import file_link_widget
from . import float_widget
from . import footage_widget
from . import list_widget
from . import multi_entity_widget
from . import number_widget
from . import percent_widget
from . import status_list_widget
from . import tags_widget
from . import text_widget
from . import thumbnail_widget
from . import timecode_widget
from . import url_template_widget