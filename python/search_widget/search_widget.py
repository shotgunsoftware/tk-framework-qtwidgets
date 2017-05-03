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
A simple search field with magnifying glass icon, hint text and clear button
"""

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .ui.search_widget import Ui_SearchWidget

class SearchWidget(QtGui.QWidget):
    """
    Search widget class
    """

    # emited when the search QTextField is being edited
    search_edited = QtCore.Signal(object)# search text
    # emited when the search QTextField has been changed (e.g. after hitting enter)
    search_changed = QtCore.Signal(object)# search text  

    def __init__(self, parent=None):
        """
        Construction

        :param parent:    The parent widget
        """
        QtGui.QWidget.__init__(self, parent)

        # set up the UI
        self._ui = Ui_SearchWidget()
        self._ui.setupUi(self)
        self.set_placeholder_text("Search...")

        # dynamically create the clear button so that we can place it over the
        # edit widget:
        self._clear_btn = QtGui.QPushButton(self._ui.search_edit)
        self._clear_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._clear_btn.setFlat(True)
        self._clear_btn.setCursor(QtCore.Qt.ArrowCursor)
        style = ("QPushButton {"
                 + "border: 0px solid;"
                 + "image: url(:/tk-framework-qtwidgets/search_widget/clear_search.png);"
                 + "width: 16;"
                 + "height: 16;"
                 + "}"
                 + "QPushButton::hover {"
                 + "image: url(:/tk-framework-qtwidgets/search_widget/clear_search_hover.png);"
                 + "}")
        self._clear_btn.setStyleSheet(style)
        self._clear_btn.hide()
        
        h_layout = QtGui.QHBoxLayout(self._ui.search_edit)
        h_layout.addStretch()
        h_layout.addWidget(self._clear_btn)
        h_layout.setContentsMargins(3, 0, 3, 0)
        h_layout.setSpacing(0)
        self._ui.search_edit.setLayout(h_layout)

        # hook up the signals:
        self._ui.search_edit.textEdited.connect(self._on_text_edited)
        self._ui.search_edit.returnPressed.connect(self._on_return_pressed)
        self._clear_btn.clicked.connect(self._on_clear_clicked)

    # @property
    def _get_search_text(self):
        """
        get the search text from the widget
        """
        text = self._ui.search_edit.text()
        return self._safe_to_string(text)
    # @search_text.setter
    def _set_search_text(self, value):
        """
        set the search text on the widget
        """
        self._ui.search_edit.setText(value)
        self._clear_btn.setVisible(bool(value))
    search_text = property(_get_search_text, _set_search_text)

    def set_placeholder_text(self, text):
        """
        Set the placeholder text for the widget

        :param text:    The text to use
        """
        # Note, setPlaceholderText is only available in recent versions of Qt.
        if hasattr(self._ui.search_edit, "setPlaceholderText"):
            self._ui.search_edit.setPlaceholderText(text)

    def clear(self):
        """
        """
        self._ui.search_edit.setText("")
        self._clear_btn.hide()

    def _on_clear_clicked(self):
        """
        Slot triggered when the clear button is clicked - clears the text
        and emits the relevant signals.
        """
        self.clear()
        self.search_changed.emit("")
        self.search_edited.emit("")

    def _on_text_edited(self):
        """
        Slot triggered when the text has been edited 
        """
        text = self.search_text
        self._clear_btn.setVisible(bool(text))
        self.search_edited.emit(text)

    def _on_return_pressed(self):
        """
        Slot triggered when return has been pressed
        """
        self.search_changed.emit(self.search_text)

    def _safe_to_string(self, value):
        """
        Safely convert the value to a string - handles
        unicode and QtCore.QString if using PyQt

        :param value:   The value to convert to a string
        :returns:       utf8 encoded string of the input value
        """
        if isinstance(value, str):
            # it's a string anyway so just return
            return value

        if isinstance(value, unicode):
            # convert to utf-8
            return value.encode("utf8")
    
        if hasattr(QtCore, "QString"):
            # running PyQt!
            if isinstance(value, QtCore.QString):
                # QtCore.QString inherits from str but supports
                # unicode, go figure!  Lets play safe and return
                # a utf-8 string
                return str(value.toUtf8())
    
        # For everything else, just return as string
        return str(value)       
        
        
        
        
        