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
from sgtk.platform.qt import QtGui

from ..sg_qicons import SGQIcon


class SGQWidget(QtGui.QWidget):
    """
    The ShotGrid widget class aims to facilitate creating consistent Qt widgets in Toolkit.

    QWidget subclasses can be handled by defining a subclass to this class. They should follow the naming
    convention:

        SG<Qt_Widget_Class_Name>

    For example, SGQToolButton.

    The SGQWidget class and its subclasses are just wrapper classes for their respective Qt widget class.
    They aim only to provide convenience to creating and managing Qt widgets, and are not meant to provide new
    functionality to the Qt classes. If additional functionality required, this class or its subclasses should
    be further subclassed.

    Using the SGQWidget classes can help manage styles more easily using .qss files, since the style can be
    applied directly to the ShotGrid widget class, and all widgets using the class will inherit the style,
    while not affecting other Qt widgets of the same base class. For example, a .qss file may include:

        SGQToolButton {
            border: none;
            padding: 4px;
        }

        SGQWidget {
            font-family: "Open Sans";
            font-style: "Regular";
        }

    This is particularly helpful if Toolkit is embedded in a DCC, where the QApplication object is shared
    with the DCC. This means we can be confident that the styles in our .qss only affect the Toolkit widgets
    (assuming the DCC does not define their own widget classes with the same name, which they are unlikely to
    do so).

    TODO add support for other QWidget subclasses. Currently only QToolButton is supported.
    """

    def __init__(
        self,
        parent,
        window_flags=None,
        layout_direction=QtGui.QBoxLayout.LeftToRight,
        child_widgets=None,
    ):
        """
        Create the widget.

        :param parent: The parent widget of this widget
        :type parent: QtGui.QWidget
        :param window_flags: The parent widget of this widget
        :type window_flags: Bit wise OR of any QtCore.Qt.WindowFlags
        :param layout_direction: The orientation of the widget layout
        :type layout_direction: QtGui.QBoxLayout.Direction
        :param child_widgets: The list of widgets to add to the layout of this widget. Use None to indicate
            adding a stretch in the layout.
        :type child_widgest: list<QtGui.QWidget>
        """

        if window_flags is None:
            super(SGQWidget, self).__init__(parent)
        else:
            super(SGQWidget, self).__init__(parent, window_flags)

        widget_layout = QtGui.QBoxLayout(layout_direction)
        self.setLayout(widget_layout)
        self.add_widgets(child_widgets)

    def add_widget(self, widget):
        """
        Add the widget to this SGQWidget layout.

        :param widget: The child widget to add
        :type widget: QtGui.QWidget
        """

        self.add_widgets([widget])

    def add_stretch(self):
        """
        Add the widget to this SGQWidget layout.

        :param widget: The child widget to add
        :type widget: QtGui.QWidget
        """

        self.add_widgets([None])

    def add_widgets(self, widgets):
        """
        Add the widgets to this SGQWidget layout.

        :param widget: The child widgets to add
        :type widget: QtGui.QWidget
        """

        if not widgets:
            return

        for widget in widgets:
            if widget is None:
                self.layout().addStretch()
            else:
                self.layout().addWidget(widget)

    def clear(self):
        """
        Clear the widget by removing and deleting all widgets from its layout.
        """

        child = self.layout().takeAt(0)
        while child:
            next_child = self.layout().takeAt(0)
            try:
                # Attemp to delete the widget attached to the layout item
                child.widget().deleteLater()
            except:
                # There was no widget to delete
                pass

            del child
            child = next_child


class SGQToolButton(QtGui.QToolButton):
    """
    ShotGrid widget class wrapper for QToolButton.
    """

    def __init__(
        self,
        parent=None,
        icon=None,
        icon_normal_off=None,
        icon_normal_on=None,
        checkable=True,
    ):
        """
        Create the tool button widget.

        :param parent: The tool button parent widget.
        :type parent: QtGui.QWidget
        :param icon: (optional) The icon to set for the tool button.
        :type icon: QtGui.QIcon
        :param icon_normal_off: (optional) The path to the icon to set for the tool button off state.
            NOTE: This will be igonred if the icon is specified.
        :type icon_normal_off: QtGui.QIcon
        :param icon_normal_on: (optional) The path to the icon to set for the tool button on state.
            NOTE: This will be igonred if the icon is specified.
        :type icon_normal_on: QtGui.QIcon
        :param checkable: Set to True to set the button as checkable.
        :type checkable: bool
        """

        super(SGQToolButton, self).__init__(parent)

        if not icon:
            icon = SGQIcon(normal_off=icon_normal_off, normal_on=icon_normal_on)

        self.setIcon(icon)
        self.setCheckable(checkable)
