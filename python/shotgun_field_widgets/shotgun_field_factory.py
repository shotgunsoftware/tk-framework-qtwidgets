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

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class ShotgunFieldFactory(object):
    __FIELD_TYPE_MAP = {}

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

    @classmethod
    def supported_fields(cls, sg_entity_type, field_names):
        """
        Returns the subset of fields from field_names that have an associated widget class.

        :param sg_entity_type: Shotgun entity type
        :param field_names: An array of Shotgun field names
        :returns: The subset of the field_names array that has associated widget classes.
        """
        supported_fields = []
        for field_name in field_names:
            data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)
            if data_type in cls.__FIELD_TYPE_MAP:
                supported_fields.append(field_name)
        return supported_fields

    @classmethod
    def get_display_class(cls, sg_entity_type, field_name):
        """
        Returns the widget class associated with the field type if it has been registered.

        :param sg_entity_type: Shotgun entity type
        :param field_name: Shotgun field name
        :returns: :class:`~PySide.QtGui.QWidget` or None if not found
        """
        data_type = shotgun_globals.get_data_type(sg_entity_type, field_name)
        if data_type not in cls.__FIELD_TYPE_MAP:
            print " Missing %s" % data_type
        return cls.__FIELD_TYPE_MAP.get(data_type)

    @classmethod
    def get_label(cls, sg_entity_type, field_name):
        """
        Returns a widget that can be used as a label for the given field.

        :param sg_entity_type: Shotgun entity type
        :param field_name: Shotgun field name
        :returns: :class:`~PySide.QtGui.QWidget` or None if not found
        """
        display_name = shotgun_globals.get_field_display_name(sg_entity_type, field_name)
        return QtGui.QLabel(display_name)


# import the actual field types to give them a chance to register
from .checkbox_widget import CheckBoxWidget
from .currency_widget import CurrencyWidget
from .date_widget import DateWidget
from .date_and_time_widget import DateAndTimeWidget
from .duration_widget import DurationWidget
from .entity_widget import EntityWidget
from .multi_entity_widget import MultiEntityWidget
from .float_widget import FloatWidget
from .file_link_widget import FileLinkWidget
from .footage_widget import FootageWidget
from .list_widget import ListWidget
from .number_widget import NumberWidget
from .percent_widget import PercentWidget
from .status_list_widget import StatusListWidget
from .text_widget import TextWidget
from .timecode_widget import TimecodeWidget
from .url_template_widget import UrlTemplateWidget
from .tags_widget import TagsWidget