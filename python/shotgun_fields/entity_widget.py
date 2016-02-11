# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Widget that represents the value of an entity field in Shotgun
"""
import sgtk
from sgtk.platform.qt import QtGui
from .shotgun_field_manager import ShotgunFieldManager

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class EntityWidget(QtGui.QLabel):
    """
    Inherited from a :class:`~PySide.QtGui.QLabel`, this class is able to
    display an entity field value as returned by the Shotgun API.
    """

    def __init__(self, parent=None, entity=None, field_name=None, bg_task_manager=None, **kwargs):
        """
        Constructor for the widget.  This method passes all keyword args except
        for those below through to the :class:`~PySide.QtGui.QLabel` it
        subclasses.

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :param entity: The Shotgun entity dictionary to pull the field value from.
        :type entity: Whatever is returned by the Shotgun API for this field

        :param field_name: Shotgun field name
        :type field_name: String

        :param bg_task_manager: The task manager the widget will use if it needs to run a task
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        QtGui.QLabel.__init__(self, parent, **kwargs)
        self.setOpenExternalLinks(True)

        self._bundle = sgtk.platform.current_bundle()

        self.set_value(entity[field_name])

    def set_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value displayed by the widget
        :type value: Shotgun entity dictionary with at least name, type, and id keys
        """
        if value is None:
            self.clear()
        else:
            self.setText(self._entity_dict_to_html(value))

    def _entity_dict_to_html(self, value):
        """
        Translate the entity dictionary to html that can be displayed in a
        :class:`~PySide.QtGui.QLabel`.

        :param value: The entity dictionary to conver to html
        :type value: An entity dictionary containing at least the name, type, and id keys
        """
        str_val = value["name"]
        entity_url = "%sdetail/%s/%d" % (self._bundle.sgtk.shotgun_url, value["type"], value["id"])
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(value["type"])
        str_val = "<img src='%s'><a href='%s'>%s</a>" % (entity_icon_url, entity_url, str_val)
        return str_val

ShotgunFieldManager.register("entity", EntityWidget)
