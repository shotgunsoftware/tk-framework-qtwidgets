# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reply_list_widget.ui'
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


from  . import resources_rc

class Ui_ReplyListWidget(object):
    def setupUi(self, ReplyListWidget):
        if not ReplyListWidget.objectName():
            ReplyListWidget.setObjectName(u"ReplyListWidget")
        ReplyListWidget.resize(418, 401)
        self.verticalLayout = QVBoxLayout(ReplyListWidget)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.reply_scroll_area = QScrollArea(ReplyListWidget)
        self.reply_scroll_area.setObjectName(u"reply_scroll_area")
        self.reply_scroll_area.setWidgetResizable(True)
        self.reply_widget = QWidget()
        self.reply_widget.setObjectName(u"reply_widget")
        self.reply_widget.setGeometry(QRect(0, 0, 414, 397))
        self.reply_layout = QVBoxLayout(self.reply_widget)
        self.reply_layout.setObjectName(u"reply_layout")
        self.reply_scroll_area.setWidget(self.reply_widget)

        self.verticalLayout.addWidget(self.reply_scroll_area)

        self.retranslateUi(ReplyListWidget)

        QMetaObject.connectSlotsByName(ReplyListWidget)
    # setupUi

    def retranslateUi(self, ReplyListWidget):
        ReplyListWidget.setWindowTitle(QCoreApplication.translate("ReplyListWidget", u"Form", None))
    # retranslateUi
