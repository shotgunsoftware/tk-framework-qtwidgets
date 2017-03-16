# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reply_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ReplyWidget(object):
    def setupUi(self, ReplyWidget):
        ReplyWidget.setObjectName("ReplyWidget")
        ReplyWidget.resize(287, 142)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(ReplyWidget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(-1, -1, 8, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.user_thumb = UserThumbnail(ReplyWidget)
        self.user_thumb.setMinimumSize(QtCore.QSize(30, 30))
        self.user_thumb.setMaximumSize(QtCore.QSize(30, 30))
        self.user_thumb.setText("")
        self.user_thumb.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.user_thumb.setObjectName("user_thumb")
        self.verticalLayout_2.addWidget(self.user_thumb)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.header_left = QtGui.QLabel(ReplyWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_left.sizePolicy().hasHeightForWidth())
        self.header_left.setSizePolicy(sizePolicy)
        self.header_left.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.header_left.setWordWrap(True)
        self.header_left.setObjectName("header_left")
        self.horizontalLayout.addWidget(self.header_left)
        self.date = QtGui.QLabel(ReplyWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy)
        self.date.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.date.setWordWrap(True)
        self.date.setObjectName("date")
        self.horizontalLayout.addWidget(self.date)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.reply = QtGui.QLabel(ReplyWidget)
        self.reply.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.reply.setWordWrap(True)
        self.reply.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.reply.setObjectName("reply")
        self.verticalLayout.addWidget(self.reply)
        self.verticalLayout.setStretch(1, 1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2.setStretch(1, 1)

        self.retranslateUi(ReplyWidget)
        QtCore.QMetaObject.connectSlotsByName(ReplyWidget)

    def retranslateUi(self, ReplyWidget):
        ReplyWidget.setWindowTitle(QtGui.QApplication.translate("ReplyWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header_left.setText(QtGui.QApplication.translate("ReplyWidget", "John Smith", None, QtGui.QApplication.UnicodeUTF8))
        self.date.setText(QtGui.QApplication.translate("ReplyWidget", "Tuesday", None, QtGui.QApplication.UnicodeUTF8))
        self.reply.setText(QtGui.QApplication.translate("ReplyWidget", "Lorem ipsum foo bar.", None, QtGui.QApplication.UnicodeUTF8))

from ..label_widgets import UserThumbnail
from . import resources_rc
