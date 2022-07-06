# Copyright (c) 2022 Autodesk, Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk, Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

sg_qwidgets = sgtk.platform.current_bundle().import_module("sg_qwidgets")


class MessageBox(sg_qwidgets.SGQDialog):
    """
    A custom class that inherits from Qt class QDialog, to provide a more flexible interface
    to creating a message box.

    The Qt QMessageBox is best for quickly displaying a message to a user and getting a
    response, but there are limitation to it. This class aims to allow more flexibility in
    how the message box is displayed:

    1. The caller can specify the order in which the buttons are displayed, by the order that
       they are added to the dialog.

    2. The 'Show Details' button will always align left with a stretch between itself and the
       rest of the buttons (instead of ending up in the middle of the buttons).

    3. The 'Show Details' button text be customized.

    4. The detailed text can always be shown (the 'Show Details' button will be hidden and the
       detailed text will always be dispalyed).

    5. There is the option to show a checkbox at the bottom of the dialog to facilitate remembering
       the option that the user selected, in order to optionally by-pass the dialog the next time.
    """

    # Dialog button roles
    (
        REJECT_ROLE,
        ACCEPT_ROLE,
        APPLY_ROLE,
        RESET_ROLE,
        ACTION_ROLE,
        HELP_ROLE,
    ) = range(6)

    def __init__(self, parent=None):
        """
        Initialize the message box and set up the UI.

        :param parent: The parent widget of this message box.
        :type parent: QWidget
        """

        super(MessageBox, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.setMinimumWidth(450)

        self._show_remember_checkbox = False
        self._always_show_details = False
        self._details_visible = False
        self._show_details_text = "Show Details..."
        self._hide_details_text = "Hide Details..."
        self._button_clicked = None

        # ------------------------------------------------------------------------------------
        # Set up the UI

        # Main dialog text
        self._text_label = sg_qwidgets.SGQLabel(self)
        self._text_label_widget = sg_qwidgets.SGQWidget(
            self, child_widgets=[self._text_label]
        )

        # Detailed text
        self._details_text = sg_qwidgets.SGQTextEdit(self)
        self._details_text.setFixedHeight(50)
        self._details_text.setReadOnly(True)
        self._details_text_widget = sg_qwidgets.SGQWidget(
            self,
            child_widgets=[self._details_text],
        )

        # The show/hide details button
        self._details_button = sg_qwidgets.SGQPushButton(self._show_details_text, self)
        self._details_button.clicked.connect(self.show_details)

        # Buttons widget
        self._buttons_widget = sg_qwidgets.SGQWidget(
            self,
            child_widgets=[self._details_button, None],
        )

        # Remember user selection checkbox
        self._remember_checkbox = sg_qwidgets.SGQCheckBox(
            "Remember my selected action", self
        )
        self._remember_checkbox_widget = sg_qwidgets.SGQWidget(
            self,
            child_widgets=[self._remember_checkbox, None],
        )

        # The main dialog layout
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self._text_label_widget)
        layout.addWidget(self._details_text_widget)
        layout.addWidget(self._buttons_widget)
        layout.addWidget(self._remember_checkbox_widget)
        self.setLayout(layout)

        # Spacing
        self.setContentsMargins(0, 0, 0, 0)

        # Initially start with the details hidden, until the details text is set
        self._details_text_widget.hide()
        self._details_button.hide()
        self._remember_checkbox_widget.setVisible(self._show_remember_checkbox)

    ###########################################################################################
    # Properties

    @property
    def button_clicked(self):
        """Get the button that was last clicked."""

        return self._button_clicked

    ###########################################################################################
    # Public functions

    def set_text(self, text):
        """
        Set the main message text.

        :param text: The message text.
        :type text: str
        """

        self._text_label.setText(text)

    def set_detailed_text(self, details):
        """
        Set the detailed message text. This will be dispalyed in a scrollable text area.

        If no details text is given, the details text widget will be hidden.

        :param details: The detailed text to display.
        :type details:str
        """

        if details:
            self._details_text.setPlainText(details)
            self._details_button.show()
        else:
            self._details_button.hide()

    def add_buttons(self, button_data):
        """
        Add the list of buttons to the message box.

        This is just a convenience function to call `add_button` for multiple buttons at a
        time.

        The button data should be a list of dictionaries containing the key-values:
            text:
                type: str
                value: The text to display on the button
            role:
                type: int
                value: The button role (see button roles defined in the MessageBox class)

        :param button_data: The list of data describing the buttons.
        :type button_data: list<dict>, required keys: text, role
        """

        buttons = []
        for data in button_data:
            buttons.append(self.add_button(data["text"], data["role"]))

        return buttons

    def add_button(self, text, role):
        """
        Add the button to the message box.

        The buttons will appear left-to-right in the order which they were added.

        :param text: The text to display on the button
        :type text: str
        :param role: The role for the button. When the button is clicked, the result will be
                     set to the button's role.
        :type role: int (see MessageBox class defined button roles)
        """

        button = sg_qwidgets.SGQPushButton(text, self)
        button.clicked.connect(
            lambda checked=False, b=button, r=role: self._handle_button_clicked(b, r)
        )

        # Add the button widget to the dialog
        self._buttons_widget.add_widget(button)

        return button

    def set_default_button(self, button):
        """
        Set the default button for the message box.

        Setting the button as the default will set the focus on the button.

        :param button: The button to set as the default
        :type button: QPushButton
        """

        button.setFocus(QtCore.Qt.OtherFocusReason)

    def set_always_show_details(self, always_show):
        """
        Set the flag indicating that the details text shoudl always be visible.

        The 'Show Details' button will be hidden and the details text widget will be
        visible no matter what.

        :param always_show: True to always show the details text, else False to show only when
                            the 'Show Details' button is clicked.
        :type always_show: bool
        """

        self._always_show_details = always_show
        self.show_details()

    def show_details(self):
        """
        Toggle the detailed text visibility.

        If the detailed text should always be shown, hide the 'Show Details' button.
        """

        if self._always_show_details:
            self._details_visible = True
            self._details_text_widget.setVisible(True)
            # Hide the button that show/hides the detailed text when it is always shown
            self._details_button.hide()

        else:
            # Make sure the details button is showing
            self._details_button.show()

            # Get the current visibility of the details text, toggle its visibility and set
            # the button text accordingly
            self._details_visible = not self._details_text.isVisible()
            self._details_text_widget.setVisible(self._details_visible)

            if self._details_visible:
                self._details_button.setText(self._hide_details_text)
            else:
                self._details_button.setText(self._show_details_text)

        # Ensure that the message box adujsts it size based on showing/hiding the text
        self.adjustSize()

    def set_show_details_text(self, text):
        """
        Set the text on the 'Show Details' button when clicking it will show the detailed text.

        :param text: The text to set to the 'Show Details' button
        :type text: str
        """

        self._show_details_text = text

        if not self._details_visible:
            self._details_button.setText(self._show_details_text)

    def set_hide_details_text(self, text):
        """
        Set the text on the 'Show Details' button when clicking it will hide the detailed text.

        :param text: The text to set to the 'Show Details' button
        :type text: str
        """

        self._hide_details_text = text

        if self._details_visible:
            self._details_button.setText(self._hide_details_text)

    def show_remember_checkbox(self, show):
        """
        Set the flag indicating whether or not to show the 'remember' checkbox.

        :param show: True to show the checkbox, else False to hide it.
        :type show: bool
        """

        self._show_remember_checkbox = show
        self._remember_checkbox_widget.setVisible(self._show_remember_checkbox)

    def set_remember_checkbox_text(self, text):
        """
        Set the text to display next to the 'remember' checkbox.

        :param text: The text to set on the checkbox
        :type text: str
        """

        self._remember_checkbox.setText(text)

    def get_remember_value(self):
        """
        Get the 'remember' checkbox value.

        :return: True if the 'remember' checkbox is checked, else False.
        :rtype: bool
        """

        if self._show_remember_checkbox:
            return self._remember_checkbox.isChecked()

        return None

    ###########################################################################################
    # Protected functions

    def _handle_button_clicked(self, button, role):
        """
        The callback triggered when one of the message box buttons are clicked.

        Set the button that was clicked for the caller to check after the message box closes.
        Set the dialog result to the button's role.

        :param button: The button that was clicked.
        :type button: QPushButton
        :param role: The role of the button that was clicked.
        :type role: int
        """

        self._button_clicked = button
        self.done(role)
