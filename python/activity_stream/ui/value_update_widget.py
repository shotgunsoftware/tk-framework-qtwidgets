# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'value_update_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ValueUpdateWidget(object):
    def setupUi(self, ValueUpdateWidget):
        ValueUpdateWidget.setObjectName("ValueUpdateWidget")
        ValueUpdateWidget.resize(299, 67)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(ValueUpdateWidget)
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setContentsMargins(20, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.user_thumb = UserThumbnail(ValueUpdateWidget)
        self.user_thumb.setMinimumSize(QtCore.QSize(30, 30))
        self.user_thumb.setMaximumSize(QtCore.QSize(30, 30))
        self.user_thumb.setText("")
        self.user_thumb.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.user_thumb.setObjectName("user_thumb")
        self.verticalLayout_3.addWidget(self.user_thumb)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.frame = QtGui.QFrame(ValueUpdateWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.header_left = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_left.sizePolicy().hasHeightForWidth())
        self.header_left.setSizePolicy(sizePolicy)
        self.header_left.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.header_left.setWordWrap(True)
        self.header_left.setObjectName("header_left")
        self.horizontalLayout.addWidget(self.header_left)
        self.date = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy)
        self.date.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.date.setWordWrap(True)
        self.date.setObjectName("date")
        self.horizontalLayout.addWidget(self.date)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.footer = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.footer.setWordWrap(True)
        self.footer.setObjectName("footer")
        self.verticalLayout.addWidget(self.footer)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addWidget(self.frame)
        self.horizontalLayout_2.setStretch(1, 1)

        self.retranslateUi(ValueUpdateWidget)
        QtCore.QMetaObject.connectSlotsByName(ValueUpdateWidget)

    def retranslateUi(self, ValueUpdateWidget):
        ValueUpdateWidget.setWindowTitle(QtGui.QApplication.translate("ValueUpdateWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header_left.setText(QtGui.QApplication.translate("ValueUpdateWidget", "John Smith", None, QtGui.QApplication.UnicodeUTF8))
        self.date.setText(QtGui.QApplication.translate("ValueUpdateWidget", "3 days ago", None, QtGui.QApplication.UnicodeUTF8))
        self.footer.setText(QtGui.QApplication.translate("ValueUpdateWidget", "asdasdasd", None, QtGui.QApplication.UnicodeUTF8))

from ..label_widgets import UserThumbnail
from . import resources_rc
