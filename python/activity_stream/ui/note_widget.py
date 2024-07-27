# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'note_widget.ui'
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

class Ui_NoteWidget(object):
    def setupUi(self, NoteWidget):
        if not NoteWidget.objectName():
            NoteWidget.setObjectName(u"NoteWidget")
        NoteWidget.resize(357, 166)
        self.horizontalLayout_2 = QHBoxLayout(NoteWidget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, 8, -1)
        self.user_thumb = UserThumbnail(NoteWidget)
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

        self.frame = QFrame(NoteWidget)
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

        self.links = QLabel(self.frame)
        self.links.setObjectName(u"links")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.links.sizePolicy().hasHeightForWidth())
        self.links.setSizePolicy(sizePolicy2)
        self.links.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.links.setWordWrap(True)

        self.verticalLayout.addWidget(self.links)

        self.content = QLabel(self.frame)
        self.content.setObjectName(u"content")
        sizePolicy2.setHeightForWidth(self.content.sizePolicy().hasHeightForWidth())
        self.content.setSizePolicy(sizePolicy2)
        self.content.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.content.setWordWrap(True)
        self.content.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.content)

        self.reply_layout = QVBoxLayout()
        self.reply_layout.setSpacing(0)
        self.reply_layout.setObjectName(u"reply_layout")
        self.reply_layout.setContentsMargins(0, 0, -1, -1)

        self.verticalLayout.addLayout(self.reply_layout)

        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(NoteWidget)

        QMetaObject.connectSlotsByName(NoteWidget)
    # setupUi

    def retranslateUi(self, NoteWidget):
        NoteWidget.setWindowTitle(QCoreApplication.translate("NoteWidget", u"Form", None))
        self.user_thumb.setText("")
        self.header_left.setText("")
        self.date.setText("")
        self.links.setText("")
        self.content.setText("")
    # retranslateUi
