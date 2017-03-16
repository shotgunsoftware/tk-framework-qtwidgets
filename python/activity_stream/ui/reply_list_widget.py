# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reply_list_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ReplyListWidget(object):
    def setupUi(self, ReplyListWidget):
        ReplyListWidget.setObjectName("ReplyListWidget")
        ReplyListWidget.resize(418, 401)
        self.verticalLayout = QtGui.QVBoxLayout(ReplyListWidget)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.reply_scroll_area = QtGui.QScrollArea(ReplyListWidget)
        self.reply_scroll_area.setWidgetResizable(True)
        self.reply_scroll_area.setObjectName("reply_scroll_area")
        self.reply_widget = QtGui.QWidget()
        self.reply_widget.setGeometry(QtCore.QRect(0, 0, 414, 397))
        self.reply_widget.setObjectName("reply_widget")
        self.reply_layout = QtGui.QVBoxLayout(self.reply_widget)
        self.reply_layout.setObjectName("reply_layout")
        self.reply_scroll_area.setWidget(self.reply_widget)
        self.verticalLayout.addWidget(self.reply_scroll_area)

        self.retranslateUi(ReplyListWidget)
        QtCore.QMetaObject.connectSlotsByName(ReplyListWidget)

    def retranslateUi(self, ReplyListWidget):
        ReplyListWidget.setWindowTitle(QtGui.QApplication.translate("ReplyListWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
