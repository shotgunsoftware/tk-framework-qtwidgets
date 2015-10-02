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
from .ui.navigation_widget import Ui_NavigationWidget

class NavigationWidget(QtGui.QWidget):
    """
    Navigation widget containing previous, home and next buttons: [H][<][>].  The
    widget keeps track of the current location within a list and emits signals
    whenever the user navigates via one of the buttons.
    
    :signal home_clicked: Emitted when someone clicks the home button
    :signal navigate(bj): Emitted when someone clicks the next or prev buttons.
        A navigation object is passed with the signal.
    """

    # Signal emitted whenever the user navigates using 
    # the 'previous'/[<] or 'next'/[>] buttons.
    navigate = QtCore.Signal(object)# destination to navigate to

    # Signal emitted whenever the 'home'/[H] button is pressed
    home_clicked = QtCore.Signal()

    class _DestinationInfo(object):
        """
        Container to keep track of information about a destination
        """
        def __init__(self, label, destination):
            """
            :param label:       The label to be used for this destination
            :param destination: The destination
            """
            self.label = label
            self.destination = destination

    def __init__(self, parent=None):
        """
        :param parent:  The parent QWidget
        :type parent:   :class:`~PySide.QtGui.QWidget`        
        """
        QtGui.QWidget.__init__(self, parent)

        self._destinations = []
        self._current_idx = 0

        # set up the UI
        self._ui = Ui_NavigationWidget()
        self._ui.setupUi(self)

        self._ui.nav_home_btn.clicked.connect(self.home_clicked)
        self._ui.nav_prev_btn.clicked.connect(self._on_nav_prev_clicked)
        self._ui.nav_next_btn.clicked.connect(self._on_nav_next_clicked)

        self._update_ui()

    def add_destination(self, label, destination):
        """
        Add a destination to the widget.  This clears any future destinations
        and sets the current destination to be the one passed in.

        :param label:       The label to be used for this destination
        :param destination: The destination object
        """
        new_destination_info = NavigationWidget._DestinationInfo(label, destination)
        self._destinations = self._destinations[:self._current_idx+1] + [new_destination_info]
        self._current_idx = len(self._destinations)-1
        self._update_ui()

    # ------------------------------------------------------------------------------------------
    # Protected methods

    def _on_nav_prev_clicked(self):
        """
        Slot triggered when the 'previous'/[<] button is clicked.  Sets the current 
        destination to the previous destination and emits the navigate signal.
        """
        if self._current_idx < 1:
            return

        self._current_idx -= 1
        destination_info = self._destinations[self._current_idx]
        self.navigate.emit(destination_info.destination)
        self._update_ui()

    def _on_nav_next_clicked(self):
        """
        Slot triggered when the 'next'/[>] button is clicked.  Sets the current 
        destination to the next destination and emits the navigate signal.
        """
        if self._current_idx >= (len(self._destinations) - 1):
            return

        self._current_idx += 1
        destination_info = self._destinations[self._current_idx]
        self.navigate.emit(destination_info.destination)
        self._update_ui()

    def _update_ui(self):
        """
        Update the UI to reflect the current state of the destination queue
        """
        self._ui.nav_home_btn.setEnabled(True)
        self._ui.nav_prev_btn.setEnabled(self._current_idx > 0)
        self._ui.nav_next_btn.setEnabled(self._current_idx < (len(self._destinations) - 1))



