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

sg_qicons = sgtk.platform.current_bundle().import_module("sg_qicons")
SGQIcon = sg_qicons.SGQIcon


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
    ShotGrid wrapper class for QCheckBox widget.
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


class SGQCheckBox(QtGui.QCheckBox):
    """
    ShotGrid wrapper class for QCheckBox widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQComboBox(QtGui.QComboBox):
    """
    ShotGrid wrapper class for QComboBox widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQCommandLinkButton(QtGui.QCommandLinkButton):
    """
    ShotGrid wrapper class for QCommandLinkButton widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQDateEdit(QtGui.QDateEdit):
    """
    ShotGrid wrapper class for QDateEdit widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQDateTimeEdit(QtGui.QDateTimeEdit):
    """
    ShotGrid wrapper class for QDateTimeEdit widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQDial(QtGui.QDial):
    """
    ShotGrid wrapper class for QDial widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQDoubleSpinBox(QtGui.QDoubleSpinBox):
    """
    ShotGrid wrapper class for QDoubleSpinBox widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQFocusFrame(QtGui.QFocusFrame):
    """
    ShotGrid wrapper class for QFocusFrame widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQFontComboBox(QtGui.QFontComboBox):
    """
    ShotGrid wrapper class for QFontComboBox widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQLCDNumber(QtGui.QLCDNumber):
    """
    ShotGrid wrapper class for QLCDNumber widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQLabel(QtGui.QLabel):
    """
    ShotGrid wrapper class for QLabel widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQLineEdit(QtGui.QLineEdit):
    """
    ShotGrid wrapper class for QLineEdit widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTextEdit(QtGui.QTextEdit):
    """
    ShotGrid wrapper class for QTextEdit widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQMenu(QtGui.QMenu):
    """
    ShotGrid wrapper class for QMenu widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQProgressBar(QtGui.QProgressBar):
    """
    ShotGrid wrapper class for QProgressBar widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQPushButton(QtGui.QPushButton):
    """
    ShotGrid wrapper class for QSGQPushButtonwidget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQRadioButton(QtGui.QRadioButton):
    """
    ShotGrid wrapper class for QRadioButton widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQScrollArea(QtGui.QScrollArea):
    """
    ShotGrid wrapper class for QScrollArea widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQScrollBar(QtGui.QScrollBar):
    """
    ShotGrid wrapper class for QScrollBar widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQSizeGrip(QtGui.QSizeGrip):
    """
    ShotGrid wrapper class for QSizeGrip widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """

    def __init__(self, parent):
        super(SGQSizeGrip, self).__init__(parent)


class SGQSlider(QtGui.QSlider):
    """
    ShotGrid wrapper class for QSlider widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQSpinBox(QtGui.QSpinBox):
    """
    ShotGrid wrapper class for QSpinBox widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTabBar(QtGui.QTabBar):
    """
    ShotGrid wrapper class for QTabBar widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTabWidget(QtGui.QTabWidget):
    """
    ShotGrid wrapper class for QTabWidget widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTimeEdit(QtGui.QTimeEdit):
    """
    ShotGrid wrapper class for QTimeEdit widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQToolBox(QtGui.QToolBox):
    """
    ShotGrid wrapper class for QToolBox widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQCalendarWidget(QtGui.QCalendarWidget):
    """
    ShotGrid wrapper class for QCalendarWidget widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQColumnView(QtGui.QColumnView):
    """
    ShotGrid wrapper class for QColumnView widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQDataWidgetMapper(QtGui.QDataWidgetMapper):
    """
    ShotGrid wrapper class for QDataWidgetMapper widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQListView(QtGui.QListView):
    """
    ShotGrid wrapper class for QListview widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTableView(QtGui.QTableView):
    """
    ShotGrid wrapper class for QTableView widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTreeView(QtGui.QTreeView):
    """
    ShotGrid wrapper class for QTreeView widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQUndoView(QtGui.QUndoView):
    """
    ShotGrid wrapper class for QUndoView widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQDialog(QtGui.QDialog):
    """
    ShotGrid wrapper class for QDialog widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQFrame(QtGui.QFrame):
    """
    ShotGrid wrapper class for QFrame widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQButtonGroup(QtGui.QButtonGroup):
    """
    ShotGrid wrapper class for QButtonGroup widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQGroupBox(QtGui.QGroupBox):
    """
    ShotGrid wrapper class for QGroupBox widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQSplitter(QtGui.QSplitter):
    """
    ShotGrid wrapper class for QSplitter widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQSplitterHandle(QtGui.QSplitterHandle):
    """
    ShotGrid wrapper class for QSplitterHandle widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """

    def __init__(self, orientation, splitter_parent):
        super(SGQSplitterHandle, self).__init__(orientation, splitter_parent)


class SGQStackedWidget(QtGui.QStackedWidget):
    """
    ShotGrid wrapper class for QStackedWidget widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQDockWidget(QtGui.QDockWidget):
    """
    ShotGrid wrapper class for QDockWidget widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQActionGroup(QtGui.QActionGroup):
    """
    ShotGrid wrapper class for QActionGroup widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQMenuBar(QtGui.QMenuBar):
    """
    ShotGrid wrapper class for QMenuBar widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQStatusBar(QtGui.QStatusBar):
    """
    ShotGrid wrapper class for QStatusBar widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQWidgetAction(QtGui.QWidgetAction):
    """
    ShotGrid wrapper class for QWidgetAction widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQToolBar(QtGui.QToolBar):
    """
    ShotGrid wrapper class for QToolBar widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQListWidget(QtGui.QListWidget):
    """
    ShotGrid wrapper class for QListWidget widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQListWidgetItem(QtGui.QListWidgetItem):
    """
    ShotGrid wrapper class for QListWidgetItem widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTableWidget(QtGui.QTableWidget):
    """
    ShotGrid wrapper class for QTableWidget widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTableWidgetItem(QtGui.QTableWidgetItem):
    """
    ShotGrid wrapper class for QTableWidgetItem widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTreeWidget(QtGui.QTreeWidget):
    """
    ShotGrid wrapper class for QTreeWidget widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """


class SGQTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    ShotGrid wrapper class for QTreeWidgetItem widget.

    No additional functionality for this wrapper class, other than declaring it as a subclass.
    """
