# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'activity_stream_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ActivityStreamWidget(object):
    def setupUi(self, ActivityStreamWidget):
        ActivityStreamWidget.setObjectName("ActivityStreamWidget")
        ActivityStreamWidget.resize(418, 401)
        self.verticalLayout = QtGui.QVBoxLayout(ActivityStreamWidget)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.activity_stream_scroll_area = QtGui.QScrollArea(ActivityStreamWidget)
        self.activity_stream_scroll_area.setWidgetResizable(True)
        self.activity_stream_scroll_area.setObjectName("activity_stream_scroll_area")
        self.activity_stream_widget = QtGui.QWidget()
        self.activity_stream_widget.setGeometry(QtCore.QRect(0, 0, 414, 397))
        self.activity_stream_widget.setObjectName("activity_stream_widget")
        self.verticalLayout_17 = QtGui.QVBoxLayout(self.activity_stream_widget)
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.activity_stream_layout_3 = QtGui.QVBoxLayout()
        self.activity_stream_layout_3.setContentsMargins(0, 0, 12, 0)
        self.activity_stream_layout_3.setObjectName("activity_stream_layout_3")
        self.note_widget = NoteInputWidget(self.activity_stream_widget)
        self.note_widget.setMinimumSize(QtCore.QSize(0, 40))
        self.note_widget.setObjectName("note_widget")
        self.activity_stream_layout_3.addWidget(self.note_widget)
        self.verticalLayout_17.addLayout(self.activity_stream_layout_3)
        self.activity_stream_layout = QtGui.QVBoxLayout()
        self.activity_stream_layout.setContentsMargins(0, 12, 12, 12)
        self.activity_stream_layout.setObjectName("activity_stream_layout")
        self.verticalLayout_17.addLayout(self.activity_stream_layout)
        self.activity_stream_scroll_area.setWidget(self.activity_stream_widget)
        self.verticalLayout.addWidget(self.activity_stream_scroll_area)

        self.retranslateUi(ActivityStreamWidget)
        QtCore.QMetaObject.connectSlotsByName(ActivityStreamWidget)

    def retranslateUi(self, ActivityStreamWidget):
        ActivityStreamWidget.setWindowTitle(QtGui.QApplication.translate("ActivityStreamWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from ..qtwidgets import NoteInputWidget
from . import resources_rc
