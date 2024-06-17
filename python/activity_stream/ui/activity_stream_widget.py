# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'activity_stream_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
from tank.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from tank.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from ..qtwidgets import NoteInputWidget
from  . import resources_rc
class Ui_ActivityStreamWidget(object):
    def setupUi(self, ActivityStreamWidget):
        if not ActivityStreamWidget.objectName():
            ActivityStreamWidget.setObjectName(u"ActivityStreamWidget")
        ActivityStreamWidget.resize(418, 401)
        self.verticalLayout = QVBoxLayout(ActivityStreamWidget)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.activity_stream_scroll_area = QScrollArea(ActivityStreamWidget)
        self.activity_stream_scroll_area.setObjectName(u"activity_stream_scroll_area")
        self.activity_stream_scroll_area.setWidgetResizable(True)
        self.activity_stream_widget = QWidget()
        self.activity_stream_widget.setObjectName(u"activity_stream_widget")
        self.activity_stream_widget.setGeometry(QRect(0, 0, 414, 397))
        self.verticalLayout_17 = QVBoxLayout(self.activity_stream_widget)
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.activity_stream_layout_3 = QVBoxLayout()
        self.activity_stream_layout_3.setObjectName(u"activity_stream_layout_3")
        self.activity_stream_layout_3.setContentsMargins(0, 0, 12, 0)
        self.note_widget = NoteInputWidget(self.activity_stream_widget)
        self.note_widget.setObjectName(u"note_widget")
        self.note_widget.setMinimumSize(QSize(0, 40))
        self.activity_stream_layout_3.addWidget(self.note_widget)
        self.verticalLayout_17.addLayout(self.activity_stream_layout_3)
        self.activity_stream_layout = QVBoxLayout()
        self.activity_stream_layout.setObjectName(u"activity_stream_layout")
        self.activity_stream_layout.setContentsMargins(0, 12, 12, 12)
        self.verticalLayout_17.addLayout(self.activity_stream_layout)
        self.activity_stream_scroll_area.setWidget(self.activity_stream_widget)
        self.verticalLayout.addWidget(self.activity_stream_scroll_area)
        self.retranslateUi(ActivityStreamWidget)
        QMetaObject.connectSlotsByName(ActivityStreamWidget)
    # setupUi
    def retranslateUi(self, ActivityStreamWidget):
        ActivityStreamWidget.setWindowTitle(QCoreApplication.translate("ActivityStreamWidget", u"Form", None))
    # retranslateUi
