# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reply_widget.ui'
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

class Ui_ReplyWidget(object):
    def setupUi(self, ReplyWidget):
        if not ReplyWidget.objectName():
            ReplyWidget.setObjectName(u"ReplyWidget")
        ReplyWidget.resize(287, 142)
        self.horizontalLayout_2 = QHBoxLayout(ReplyWidget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 10, 0, 2)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, 8, -1)
        self.user_thumb = UserThumbnail(ReplyWidget)
        self.user_thumb.setObjectName(u"user_thumb")
        self.user_thumb.setMinimumSize(QSize(30, 30))
        self.user_thumb.setMaximumSize(QSize(30, 30))
        self.user_thumb.setPixmap(QPixmap(u":/tk_framework_qtwidgets.activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.verticalLayout_2.addWidget(self.user_thumb)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Ignored)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout_2.setStretch(1, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.header_left = QLabel(ReplyWidget)
        self.header_left.setObjectName(u"header_left")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_left.sizePolicy().hasHeightForWidth())
        self.header_left.setSizePolicy(sizePolicy)
        self.header_left.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.header_left.setWordWrap(True)

        self.horizontalLayout.addWidget(self.header_left)

        self.date = QLabel(ReplyWidget)
        self.date.setObjectName(u"date")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy1)
        self.date.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)
        self.date.setWordWrap(True)

        self.horizontalLayout.addWidget(self.date)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.reply = QLabel(ReplyWidget)
        self.reply.setObjectName(u"reply")
        self.reply.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.reply.setWordWrap(True)
        self.reply.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.reply)

        self.verticalLayout.setStretch(1, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_2.setStretch(1, 1)

        self.retranslateUi(ReplyWidget)

        QMetaObject.connectSlotsByName(ReplyWidget)
    # setupUi

    def retranslateUi(self, ReplyWidget):
        ReplyWidget.setWindowTitle(QCoreApplication.translate("ReplyWidget", u"Form", None))
        self.user_thumb.setText("")
        self.header_left.setText(QCoreApplication.translate("ReplyWidget", u"John Smith", None))
        self.date.setText(QCoreApplication.translate("ReplyWidget", u"Tuesday", None))
        self.reply.setText(QCoreApplication.translate("ReplyWidget", u"Lorem ipsum foo bar.", None))
    # retranslateUi
