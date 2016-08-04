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

class SelectionContextMenu(QtGui.QMenu):
    """
    A QMenu that accepts action definitions defining a callback, a string
    display name, and a "required_selection" setting defining whether the
    action is enabled for single selections, multi selections, or either.
    Each action is enabled or disabled according to its selection
    requirements and the reported number of selected items.
    """
    def __init__(self, selected_entities, *args, **kwargs):
        """
        Constructs a new SelectionContextMenu.

        :param selected_entities:   The currently-selected entities.
        :type selected_entities:    A list of Shotgun entity dicts.
        """
        super(SelectionContextMenu, self).__init__(*args, **kwargs)
        self._selected_entities = selected_entities
        self._actions = dict()

    def addAction(self, action_definition):
        """
        Adds an action to the context menu.

        Action definitions passed in must take the following form:

            dict(
                callback=callable,
                text=str,
                required_selection="single"
            )

        Where the callback is a callable object that expects to receive
        a list of Version entity dictionaries as returned by the Shotgun
        Python API. The text key contains the string labels of the action
        in the QMenu, and the required_selection is one of "single", "multi",
        or "either". Any action requiring a "single" selection will be enabled
        only if there is a single item selected in the Version list view,
        those requiring "multi" selection require 2 or more selected items,
        and the "either" requirement results in the action being enabled if
        one or more items are selected.

        :param action_definition:   The action defition to add to the menu.
                                    This takes the form of a dictionary of
                                    a structure described in the method docs
                                    above.
        :type action_definition:    dict

        :returns:                   :class:`QtGui.QAction`
        """
        action = QtGui.QAction(action_definition.get("text"), self)
        num_selected = len(self._selected_entities)
        required_selection = action_definition.get("required_selection")

        # Now we can enable or disable the action according to
        # how many items have been reported as being selected.
        if not num_selected:
            action.setEnabled(False)
        elif required_selection == "single":
            action.setEnabled((num_selected == 1))
        elif required_selection == "multi":
            action.setEnabled((num_selected > 1))
        elif required_selection == "either":
            action.setEnabled(True)
        else:
            # This shouldn't ever happen.
            action.setEnabled(False)

        self._actions[action] = action_definition
        return super(SelectionContextMenu, self).addAction(action)

    def execute_callback(self, action):
        """
        Execute's the given action's callback method, as defined when
        it was added to the menu using addAction.

        :param action:  The QAction to use when looking up which callback
                        to execute.
        """
        if action:
            callback = self._actions[action]["callback"]
            callback(self._selected_entities)


        