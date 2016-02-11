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
Widget that represents the value of a multi_entity field in Shotgun
"""
from .shotgun_field_manager import ShotgunFieldManager
from .entity_widget import EntityWidget


class MultiEntityWidget(EntityWidget):
    """
    Inherited from a :class:`~EntityWidget`, this class is able to
    display a multi_entity field value as returned by the Shotgun API.
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
        EntityWidget.__init__(self, parent, entity, field_name, bg_task_manager, **kwargs)
        self.set_value(entity[field_name])

    def set_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value displayed by the widget
        :type value: A list of Shotgun entity dictionaries, each with at least keys for name, type, and id
        """
        if value is None:
            self.clear()
        else:
            self.setText(", ".join([self._entity_dict_to_html(entity) for entity in value]))

ShotgunFieldManager.register("multi_entity", MultiEntityWidget)
