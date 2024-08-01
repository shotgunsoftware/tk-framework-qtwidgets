# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_item_widget.ui'
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
from ..qtwidgets import ShotgunPlaybackLabel

from  . import resources_rc

class Ui_NewItemWidget(object):
    def setupUi(self, NewItemWidget):
        if not NewItemWidget.objectName():
            NewItemWidget.setObjectName(u"NewItemWidget")
        NewItemWidget.resize(342, 222)
        self.horizontalLayout_2 = QHBoxLayout(NewItemWidget)
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.user_thumb = UserThumbnail(NewItemWidget)
        self.user_thumb.setObjectName(u"user_thumb")
        self.user_thumb.setMinimumSize(QSize(50, 50))
        self.user_thumb.setMaximumSize(QSize(50, 50))
        self.user_thumb.setPixmap(QPixmap(u":/tk_framework_qtwidgets.activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.verticalLayout_2.addWidget(self.user_thumb)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.frame = QFrame(NewItemWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
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

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.details_thumb = ShotgunPlaybackLabel(self.frame)
        self.details_thumb.setObjectName(u"details_thumb")
        self.details_thumb.setMinimumSize(QSize(256, 144))
        self.details_thumb.setMaximumSize(QSize(256, 144))
        self.details_thumb.setPixmap(QPixmap(u":/tk_framework_qtwidgets.activity_stream/rect_256x144.png"))
        self.details_thumb.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.verticalLayout.addWidget(self.details_thumb)

        self.footer = QLabel(self.frame)
        self.footer.setObjectName(u"footer")
        self.footer.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.footer.setWordWrap(True)
        self.footer.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.footer)

        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(NewItemWidget)

        QMetaObject.connectSlotsByName(NewItemWidget)
    # setupUi

    def retranslateUi(self, NewItemWidget):
        NewItemWidget.setWindowTitle(QCoreApplication.translate("NewItemWidget", u"Form", None))
        self.user_thumb.setText("")
        self.header_left.setText(QCoreApplication.translate("NewItemWidget", u"John Smith", None))
        self.date.setText(QCoreApplication.translate("NewItemWidget", u"3 days ago", None))
        self.details_thumb.setText("")
        self.footer.setText(QCoreApplication.translate("NewItemWidget", u"description", None))
    # retranslateUi
