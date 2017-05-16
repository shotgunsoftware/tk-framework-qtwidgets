# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
from sgtk.platform.qt import QtCore, QtGui


class ShotgunSearchWidget(QtGui.QLineEdit):
    """
    A QT Widget deriving from :class:`~PySide.QtGui.QLineEdit` that creates
    a search input box with auto completion.

    The derived classes are expected to provide a :class:`PySide.QtGui.QCompleter`
    during initialization. The completer must have ``search(str)`` and ``destroy`` method.
    """
    def __init__(self, parent):
        """
        :param parent: Qt parent object
        :type parent: :class:`~PySide.QtGui.QWidget`
        """

        # first, call the base class and let it do its thing.
        super(ShotgunSearchWidget, self).__init__(parent)

        # trigger the completer to popup as text changes
        self.textEdited.connect(self._search_edited)

        # Taken from https://wiki.qt.io/Delay_action_to_wait_for_user_interaction
        self._delay_timer = QtCore.QTimer(self)
        self._delay_timer.timeout.connect(self._typing_timeout)
        self._delay_timer.setSingleShot(True)

        # FIXME: The following was stolen from SearchWidget. We can't refactor easily that
        # part of the code since the base classes for ShotgunSearchWidget and SearchWidget
        # are not the same, but at least the ShotgunSearchWidget has feature parity.
        self.set_placeholder_text("Search")

        # dynamically create the clear button so that we can place it over the
        # edit widget:
        self._clear_btn = QtGui.QPushButton(self)
        self._clear_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._clear_btn.setFlat(True)
        self._clear_btn.setCursor(QtCore.Qt.ArrowCursor)

        # Loads the style sheet for the search button.
        qss_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "search_style.qss")
        with open(qss_file, "rt") as f:
            # apply to widget (and all its children)
            self._clear_btn.setStyleSheet(f.read())

        self._clear_btn.hide()

        h_layout = QtGui.QHBoxLayout(self)
        h_layout.addStretch()
        h_layout.addWidget(self._clear_btn)
        h_layout.setContentsMargins(3, 0, 3, 0)
        h_layout.setSpacing(0)
        self.setLayout(h_layout)
        self._clear_btn.clicked.connect(self._on_clear_clicked)

    def set_placeholder_text(self, text):
        """
        Set the placeholder text for the widget

        :param text:    The text to use
        """
        # Note, setPlaceholderText is only available in recent versions of Qt.
        if hasattr(self, "setPlaceholderText"):
            self.setPlaceholderText(text)

    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.

        :param task_manager: Background task manager to use
        :type  task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager`
        """
        self.completer().set_bg_task_manager(task_manager)

    def _search_edited(self, text):
        """
        Called every time the user types something in the search box.
        """
        # This will fire _typing_timeout after 300 ms. If the user types something before it fires,
        # the timer restarts counting. This differs from the editingFinished event on a QLineEdit which
        # fires only when the user pressed enter. This fires when the user has finished typing for
        # a short period of time.
        self._clear_btn.setVisible(bool(text))
        self._delay_timer.start(300)

    def _typing_timeout(self):
        """
        Launches the search in the completer.
        """
        self.completer().search(self.text())

    def destroy(self):
        """
        Should be called before the widget is closed.
        """
        self.completer().destroy()

    def clear(self):
        """
        Clears the search box.
        """
        self.setText("")
        self._clear_btn.hide()

    def _on_clear_clicked(self):
        """
        Slot triggered when the clear button is clicked - clears the text
        and emits the relevant signals.
        """
        self.clear()

    def keyPressEvent(self, event):
        """
        Clears the line edit when the user hits escape.
        """
        if event.key() == QtCore.Qt.Key_Escape:
            self.clear()
            self.completer().popup().close()
        else:
            super(ShotgunSearchWidget, self).keyPressEvent(event)
