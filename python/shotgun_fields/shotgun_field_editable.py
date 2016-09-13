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
from .ui import resources_rc

# This is the stylesheet applied to edit, apply, and done buttons.
BUTTON_STYLE = "background-color: none; border: none; min-width: 15px;"

class ShotgunFieldEditable(QtGui.QStackedWidget):
    """
    Wraps ``DISPLAY`` and ``EDITOR`` widgets into a :class:`~PySide.QtGui.QStackedWidget`
    instance to allow toggling between the two modes.

    The class exposes the same public interface as individual field display and
    editor widgets.
    """

    # forwarded from either of the enclosed widgets values changing
    value_changed = QtCore.Signal()

    def __init__(self, display_widget, editor_widget, parent=None):
        """
        Initialize the editable widget with the display and editor instances.

        :param display_widget: The ``DISPLAY`` widget instance
        :type display_widget: :class:`~PySide.QtGui.QWidget`
        :param editor_widget: The ``EDITOR`` widget instance
        :type editor_widget: :class:`~PySide.QtGui.QWidget`
        :param parent: The parent widget or ``None``
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        super(ShotgunFieldEditable, self).__init__(parent)

        self._enabled = True

        self._display = _DisplayWidget(display_widget)
        self._editor = _EditorWidget(editor_widget)

        self._display_index = self.addWidget(self._display)
        self._edit_index = self.addWidget(self._editor)

        # ---- connect signals

        # user clicked the button to edit the value
        self._display.edit_requested.connect(
            lambda: self.setCurrentWidget(self._editor))

        # user is done editing
        self._editor.done_editing.connect(
            lambda: self.setCurrentWidget(self._display))

        # apply the new value entered into the editor
        self._editor.edit_widget.value_changed.connect(self._apply_value)

        # react to the current widget being changed
        self.currentChanged.connect(self._on_current_changed)

        # forward the value change signal from the display widget value changing.
        # because the editor widget currently applies its changed value to the
        # display widget, this should handle a value change from either widget.
        # if this widget is modified to wait on applying the new value until
        # after SG has been update, this logic will need to change.
        self._display.display_widget.value_changed.connect(
            self.value_changed.emit)

    def destroy(self):
        """
        Call to ensure proper destruction of contained widgets.
        """

        self._display.display_widget.destroy()
        self._editor.edit_widget.destroy()

    def enable_editing(self, enable):
        """
        For consistency, allow the calling code to enable/disable editing.

        Calling this method with a value of ``False`` will force the display
        widget to be shown and the edit button to be hidden. A value of ``True``
        will allow the edit button to be displayed again on mouse over.

        :param enable: ``True`` if editing should be enabled, ``False`` otherwise.
        """

        self._enabled = enable

        # if editing turned off, force the display widget to be shown
        if not self._enabled:
            self.setCurrentWidget(self._display)

        # make sure display widget follows
        self._display.enable_editing(self._enabled)

    def get_entity(self):
        """
        Returns the entity of the widget (display or editor) currently being shown.
        """
        if self.currentWidget() == self._display:
            return self._display.display_widget.get_entity()
        else:
            return self._editor.edit_widget.get_entity()

    def get_entity_type(self):
        """
        Returns the entity type of the widget (display or editor) currently being shown.
        """
        if self.currentWidget() == self._display:
            return self._display.display_widget.get_entity_type()
        else:
            return self._editor.edit_widget.get_entity_type()

    def get_field_name(self):
        """
        Returns the field name of the widget (display or editor) currently being shown.
        """
        if self.currentWidget() == self._display:
            return self._display.display_widget.get_field_name()
        else:
            return self._editor.edit_widget.get_field_name()

    def get_value(self):
        """
        Returns the value of the widget (display or editor) currently being shown.
        """
        if self.currentWidget() == self._display:
            return self._display.display_widget.get_value()
        else:
            return self._editor.edit_widget.get_value()

    def set_value(self, value):
        """
        Set the value of the widget (display or editor) currently being shown.

        .. note:: Calling this method while the editor is displayed will trigger
            the value to be accepted and applied. The display widget will
            automatically be shown.

        This widget's ``value_changed()`` signal will also be emitted.
        """
        if self.currentWidget() == self._display:
            return self._display.display_widget.set_value(value)
        else:
            return self._editor.edit_widget.set_value(value)

    def minimumSizeHint(self):
        """
        Returns the minimum size hint for the currently displayed widget
        """
        return self.currentWidget().minimumSizeHint()

    def sizeHint(self):
        """
        Returns the size hint for the currently displayed widget
        """
        return self.currentWidget().sizeHint()

    def _apply_value(self):
        """
        Apply the editor's current value to the display widget and finish editing.
        """
        new_value = self._editor.edit_widget.get_value()
        self._display.display_widget.set_value(new_value)
        self.setCurrentWidget(self._display)

    def _on_current_changed(self, index):
        """
        Primarily used to ensure focus and to make sure the display/edit widgets are in sync.

        :param int index: The index of the newly current widget in the stack.
        """

        if index == self._edit_index:
            try:
                self._editor.edit_widget.blockSignals(True)
                self._editor.edit_widget.set_value(
                    self._display.display_widget.get_value()
                )
            finally:
                self._editor.edit_widget.blockSignals(False)

            if hasattr(self._editor.edit_widget, '_begin_edit'):
                self._editor.edit_widget._begin_edit()

        self.currentWidget().setFocus()


class ShotgunFieldNotEditable(QtGui.QWidget):
    """
    Simplified wrapper that indicates a field is not editable.

    Adds a "no edit" icon when the supplied ``DISPLAY`` widget is hovered.
    """

    # forward from the wrapped widget
    value_changed = QtCore.Signal()

    def __init__(self, display_widget, parent=None):
        """
        Initialize the widget.

        :param display_widget: The ``DISPLAY`` widget instance
        :type display_widget: :class:`~PySide.QtGui.QWidget`
        :param parent: The parent widget or ``None``
        :type parent: :class:`~PySide.QtGui.QWidget`
        """

        super(ShotgunFieldNotEditable, self).__init__(parent)

        self._display_widget = display_widget

        # this is the "no edit" label that will show on hover
        self._no_edit_lbl = QtGui.QLabel(self)
        self._no_edit_lbl.setPixmap(
            QtGui.QPixmap(":/qtwidgets-shotgun-fields/not_editable.png"))
        self._no_edit_lbl.setFixedSize(QtCore.QSize(16, 16))
        self._no_edit_lbl.hide()

        spacer = QtGui.QWidget()
        spacer.setFixedHeight(self._no_edit_lbl.height())
        spacer.setFixedWidth(4)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(display_widget)
        layout.addWidget(spacer)
        layout.addWidget(self._no_edit_lbl)
        layout.addStretch(10)

        self.installEventFilter(self)

        # forward the display widget's value changed signal
        self._display_widget.value_changed.connect(self.value_changed.emit)

    def enable_editing(self, enable):
        """
        This method exists to allow this object to conform to the ``EDITABLE``
        widget protocol.

        Because this is a field that isn't editable however, this method does
        nothing.
        """
        pass

    def eventFilter(self, obj, event):
        """
        Filter mouse enter/leave events in order to show/hide the "no edit" label.
        """
        if event.type() == QtCore.QEvent.Enter:
            self._no_edit_lbl.show()
        elif event.type() == QtCore.QEvent.Leave:
            self._no_edit_lbl.hide()

        return False

    def __getattr__(self, name):
        """
        Routes any attributes not found on the widget to the fields widget that
        it is wrapping.
        """
        return getattr(self._display_widget, name)


class _DisplayWidget(QtGui.QWidget):
    """
    A wrapper around a display widget with a hoverable "edit" button.
    """

    edit_requested = QtCore.Signal()

    def __init__(self, display_widget, parent=None):
        """
        Initialize the wrapper widget.

        :param display_widget: The ``DISPLAY`` widget instance
        :type display_widget: :class:`~PySide.QtGui.QWidget`
        :param parent: The parent widget instance or None
        :type parent: :class:`~PySide.QtGui.QWidget`
        :return:
        """

        super(_DisplayWidget, self).__init__(parent)

        self._enabled = True

        self._display_widget = display_widget

        self._edit_btn = QtGui.QPushButton()
        self._edit_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/edit_field.png"))
        self._edit_btn.setFixedSize(QtCore.QSize(16, 16))
        self._edit_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self._edit_btn.hide()

        # make sure there's never a bg color or border
        self._edit_btn.setStyleSheet(BUTTON_STYLE)

        spacer = QtGui.QWidget()
        spacer.setFixedHeight(self._edit_btn.height())
        spacer.setFixedWidth(4)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(display_widget)
        layout.addWidget(spacer)
        layout.addWidget(self._edit_btn)
        layout.addStretch(10)

        self.setMinimumHeight(self._edit_btn.height())

        self.installEventFilter(self)

        # ---- connect singals

        self._edit_btn.clicked.connect(lambda: self.edit_requested.emit())

    def eventFilter(self, obj, event):
        """
        Filter out mouse enter/leave events in order to show/hide the edit button.
        """

        # only worry about showing the edit button if editing is enabled
        if self._enabled:
            if event.type() == QtCore.QEvent.Enter:
                self._edit_btn.show()
            elif event.type() == QtCore.QEvent.Leave:
                self._edit_btn.hide()

        return False

    def enable_editing(self, enable):
        """
        Calling this method with a value of ``False`` will force the edit button
        to be hidden. A value of ``True`` will allow the edit button to be
        displayed again on mouse over.

        :param enable: ``True`` if editing should be enabled, ``False`` otherwise.
        """

        self._enabled = enable

        # force hide the edit button if editing turned off
        if not self._enabled:
            self._edit_btn.hide()

    @property
    def display_widget(self):
        """Convenience property to access the display widget"""
        return self._display_widget


class _EditorWidget(QtGui.QWidget):
    """
    Wrapper around the editor widget to display "done" and "apply" buttons

    :signal: ``done_editing()`` emitted when the editor is ready to be closed

    """

    done_editing = QtCore.Signal()

    def __init__(self, editor_widget, parent=None):
        """
        Initialize the wrapper widget.

        :param editor_widget: The ``EDITOR`` widget instance
        :type editor_widget: :class:`~PySide.QtGui.QWidget`
        :param parent: The parent widget instance or None
        :type parent: :class:`~PySide.QtGui.QWidget`
        :return:
        """
        super(_EditorWidget, self).__init__(parent)
        self._editor_widget = editor_widget
        self._editor_widget.setFocusPolicy(QtCore.Qt.StrongFocus)

        self._done_btn = QtGui.QPushButton()
        self._done_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/edit_close.png"))
        self._done_btn.setFixedSize(QtCore.QSize(16, 16))
        self._done_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        self._apply_btn = QtGui.QPushButton()
        self._apply_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/apply_value.png"))
        self._apply_btn.setFixedSize(QtCore.QSize(16, 16))
        self._apply_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        # make sure there's never a bg color or border
        self._done_btn.setStyleSheet(BUTTON_STYLE)
        self._apply_btn.setStyleSheet(BUTTON_STYLE)

        if self._editor_widget.sizeHint().height() >= 32:
            btn_layout = QtGui.QVBoxLayout()
            btn_layout.addWidget(self._done_btn)
            btn_layout.addStretch()
            btn_layout.addWidget(self._apply_btn)
        else:
            btn_layout = QtGui.QHBoxLayout()
            btn_layout.addWidget(self._apply_btn)
            btn_layout.addWidget(self._done_btn)
            btn_layout.addStretch()

        if getattr(editor_widget, '_IMMEDIATE_APPLY', None):
            # widget is set to immediately apply value. no need to display the btn
            self._apply_btn.hide()

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(editor_widget)
        layout.addLayout(btn_layout)
        layout.addStretch()

        layout.setAlignment(self._done_btn, QtCore.Qt.AlignBottom)

        self.installEventFilter(self)

        # ---- connect singals

        self._done_btn.clicked.connect(lambda: self.done_editing.emit())
        self._apply_btn.clicked.connect(self._apply_value)

    def eventFilter(self, obj, event):
        """
        Capture the Escape key to emit the ``done_editing`` signal.
        """
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self.done_editing.emit()
                return True

        return False

    def setFocus(self):
        """
        Override the default behavior to give focus to the editor widget.
        """
        self._editor_widget.setFocus()

    @property
    def edit_widget(self):
        """Convenience property to access the editor widget"""
        return self._editor_widget

    def _apply_value(self):
        """
        Called when the "apply" button is clicked.

        Make sure the edit widget's value is updated and emit the
        ``done_editing`` signal.
        """
        # TODO: rather than doing this weird setting of its own value, this
        # should simply emit a 'value_changed' signal. the widgets should be
        # responsible for storing their own values as they are modified
        self.edit_widget.set_value(self.edit_widget.get_value())
        self.done_editing.emit()



