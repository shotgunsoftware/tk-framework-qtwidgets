# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'simple_new_item_widget.ui'
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

from ..label_widgets import UserThumbnail
from  . import resources_rc
class Ui_SimpleNewItemWidget(object):
    def setupUi(self, SimpleNewItemWidget):
        if not SimpleNewItemWidget.objectName():
            SimpleNewItemWidget.setObjectName(u"SimpleNewItemWidget")
        SimpleNewItemWidget.resize(182, 46)
        self.horizontalLayout_2 = QHBoxLayout(SimpleNewItemWidget)
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(20, 0, 0, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.user_thumb = UserThumbnail(SimpleNewItemWidget)
        self.user_thumb.setObjectName(u"user_thumb")
        self.user_thumb.setMinimumSize(QSize(30, 30))
        self.user_thumb.setMaximumSize(QSize(30, 30))
        self.user_thumb.setPixmap(QPixmap(u":/tk_framework_qtwidgets.activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.verticalLayout_3.addWidget(self.user_thumb)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.frame = QFrame(SimpleNewItemWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.header_left = QLabel(self.frame)
        self.header_left.setObjectName(u"header_left")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_left.sizePolicy().hasHeightForWidth())
        self.header_left.setSizePolicy(sizePolicy)
        self.header_left.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.header_left.setWordWrap(True)
        self.horizontalLayout.addWidget(self.header_left)
        self.date = QLabel(self.frame)
        self.date.setObjectName(u"date")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy1)
        self.date.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)
        self.date.setWordWrap(True)
        self.horizontalLayout.addWidget(self.date)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addWidget(self.frame)
        self.horizontalLayout_2.setStretch(1, 1)
        self.retranslateUi(SimpleNewItemWidget)
        QMetaObject.connectSlotsByName(SimpleNewItemWidget)
    # setupUi
    def retranslateUi(self, SimpleNewItemWidget):
        SimpleNewItemWidget.setWindowTitle(QCoreApplication.translate("SimpleNewItemWidget", u"Form", None))
        self.user_thumb.setText("")
        self.header_left.setText("")
        self.date.setText("")
    # retranslateUi
