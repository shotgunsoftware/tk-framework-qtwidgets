# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# XXX docs


import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui import resources_rc

class ShotgunFieldEditable(QtGui.QStackedWidget):

    def __init__(self, display_widget, editor_widget, parent=None):

        super(ShotgunFieldEditable, self).__init__(parent)

        self._display = _DisplayWidget(display_widget)
        self._editor = _EditorWidget(editor_widget)

        self._display_index = self.addWidget(self._display)
        self._edit_index = self.addWidget(self._editor)

        # ---- connect signals

        self._display.edit_requested.connect(
            lambda: self.setCurrentWidget(self._editor))

        self._editor.done_editing.connect(
            lambda: self.setCurrentWidget(self._display))

        # XXX document the `editing_finished` signal in meta class
        if hasattr(self._editor.edit_widget, 'editing_finished'):
            self._editor.edit_widget.editing_finished.connect(
                lambda: self.setCurrentWidget(self._display)
            )

        self.currentChanged.connect(self.on_current_changed)


    def on_current_changed(self, index):

        for i in range(0, self.count()):
            if i == index:
                self.widget(i).show()
            else:
                self.widget(i).hide()

        self.currentWidget().setFocus()

    def sizeHint(self):
        return self.currentWidget().sizeHint()

    def minimumSizeHint(self):
        return self.currentWidget().minimumSizeHint()

class _DisplayWidget(QtGui.QWidget):

    edit_requested = QtCore.Signal()

    def __init__(self, display_widget, parent=None):

        super(_DisplayWidget, self).__init__(parent)

        self._display_widget = display_widget

        self._edit_btn = QtGui.QPushButton()
        self._edit_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/edit_field.png"))
        self._edit_btn.setFixedSize(QtCore.QSize(16, 16))
        self._edit_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self._edit_btn.hide()

        # make sure there's never a bg color or border
        self._edit_btn.setStyleSheet("background-color: none; border: none;")

        spacer = QtGui.QWidget()
        spacer.setFixedHeight(self._edit_btn.height())
        spacer.setFixedWidth(2)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(display_widget)
        layout.addWidget(spacer)
        layout.addWidget(self._edit_btn)
        layout.addStretch(10)


        #self.setMinimumHeight(self._edit_btn.height())

        self.installEventFilter(self)

        # ---- connect singals

        self._edit_btn.clicked.connect(lambda: self.edit_requested.emit())

    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.Enter:
            self._edit_btn.show()
        elif event.type() == QtCore.QEvent.Leave:
            self._edit_btn.hide()

        return False

    @property
    def display_widget(self):
        return self._display_widget

class _EditorWidget(QtGui.QWidget):

    done_editing = QtCore.Signal()

    def __init__(self, editor_widget, parent=None):

        super(_EditorWidget, self).__init__(parent)
        self._editor_widget = editor_widget
        self._editor_widget.setFocusPolicy(QtCore.Qt.StrongFocus)

        self._done_btn = QtGui.QPushButton()
        self._done_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/edit_close.png"))
        self._done_btn.setFixedSize(QtCore.QSize(16, 16))
        self._done_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        # make sure there's never a bg color or border
        self._done_btn.setStyleSheet("background-color: none; border: none;")

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(editor_widget)
        layout.addWidget(self._done_btn)
        layout.addStretch()

        #self.setMinimumHeight(self._done_btn.height())

        self.installEventFilter(self)

        # ---- connect singals

        self._done_btn.clicked.connect(lambda: self.done_editing.emit())

    def setFocus(self):
        self._editor_widget.setFocus()

    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self.done_editing.emit()
                return True

        return False

    @property
    def edit_widget(self):
        return self._editor_widget

