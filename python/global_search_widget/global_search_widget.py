# Copyright (c) 2015 Shotgun Software Inc.
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

global_search_copmleter = sgtk.platform.current_bundle().import_module(
    "global_search_completer")

class GlobalSearchWidget(QtGui.QLineEdit):
    """
    A QT Widget deriving from :class:`~PySide.QtGui.QLineEdit` that creates
    a global search input box with auto completion.
    
    :signal: ``entity_selected(str, int)`` - Fires when someone selects an entity inside
            the search results. The returned parameters are entity type and entity id.
    """

    # emitted when shotgun has been updated
    entity_selected = QtCore.Signal(str, int)

    def __init__(self, parent):
        """
        :param parent: Qt parent object
        :type parent: :class:`~PySide.QtGui.QWidget`        
        """
 
        # first, call the base class and let it do its thing.
        super(GlobalSearchWidget, self).__init__(parent)

        # configure our popup completer
        self.setCompleter(global_search_copmleter.GlobalSearchCompleter(self))

        # trigger the completer to popup as text changes
        self.textEdited.connect(self.completer().search)

        # forward the completer's selected signal
        self.completer().entity_selected.connect(self.entity_selected.emit)
        
    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.
        
        :param task_manager: Background task manager to use
        :type  task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager` 
        """
        self.completer().set_bg_task_manager(task_manager)

    def set_searchable_entity_types(self, types_dict):
        """
        Specify a dictionary of entity types with optional search filters to
        limit the breadth of the widget's search.

        See the documentation for `GlobalSearchCompleter.set_searchable_entity_types`
        for the default values if this method is not called on the widget.

        :param types_dict: A dictionary of searchable types with optional filters
        """

        self.completer().set_searchable_entity_types(types_dict)

    def destroy(self):
        """
        Should be called before the widget is closed
        """
        self.completer().destroy()

