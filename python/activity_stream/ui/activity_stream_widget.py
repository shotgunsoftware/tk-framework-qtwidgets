# -*- coding: utf-8 -*-

# Form implementation ORIGINALLY generated from reading ui file 'activity_stream_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# *******  NOT USING QT DESIGNER FOR THIS TEMPORARILY

from tank.platform.qt import QtCore, QtGui

class Ui_ActivityStreamWidget(object):
    # make a 418x401 ActivityStreanWidget
    # make verticalLayout
    # make scroll area inside ActivityStreamWidget
    # make qwidget activity_stream_widget
    # make another vBox, verticalLaout_17 inside the activity_stream_widget
    # make yet another vBox called activity_stream_layout_3
    # make NoteInputWidget inside of activity_stream_widget
    # add note_widget to activity_stream_layout_3
    # add activity_stream_layout_3 inside of verticalLaout_17

    # so basically we care about note_widget, activity_stream_widget, which are stacked upon each other

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
        
        # this is mostly covered by other widgets
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
