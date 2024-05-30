# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'shotgun_folder_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
from sgtk.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from sgtk.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from  . import resources_rc
class Ui_ShotgunFolderWidget(object):
    def setupUi(self, ShotgunFolderWidget):
        if not ShotgunFolderWidget.objectName():
            ShotgunFolderWidget.setObjectName(u"ShotgunFolderWidget")
        ShotgunFolderWidget.resize(564, 512)
        self.verticalLayout = QVBoxLayout(ShotgunFolderWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.box = QFrame(ShotgunFolderWidget)
        self.box.setObjectName(u"box")
        self.box.setFrameShape(QFrame.StyledPanel)
        self.box.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.box)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.thumbnail_layout = QHBoxLayout()
        self.thumbnail_layout.setObjectName(u"thumbnail_layout")
        self.thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        self.thumbnail = QLabel(self.box)
        self.thumbnail.setObjectName(u"thumbnail")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thumbnail.sizePolicy().hasHeightForWidth())
        self.thumbnail.setSizePolicy(sizePolicy)
        self.thumbnail.setMinimumSize(QSize(0, 0))
        self.thumbnail.setMaximumSize(QSize(16777215, 16777215))
        self.thumbnail.setPixmap(QPixmap(u":/tk-framework-qtwidgets/shotgun_widget/rect_512x400.png"))
        self.thumbnail.setScaledContents(False)
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.thumbnail_layout.addWidget(self.thumbnail)
        self.verticalLayout_2.addLayout(self.thumbnail_layout)
        self.header_layout = QHBoxLayout()
        self.header_layout.setObjectName(u"header_layout")
        self.header_layout.setContentsMargins(-1, 0, -1, -1)
        self.header = QLabel(self.box)
        self.header.setObjectName(u"header")
        self.header_layout.addWidget(self.header)
        self.button = QToolButton(self.box)
        self.button.setObjectName(u"button")
        self.header_layout.addWidget(self.button)
        self.verticalLayout_2.addLayout(self.header_layout)
        self.body = QLabel(self.box)
        self.body.setObjectName(u"body")
        self.verticalLayout_2.addWidget(self.body)
        self.verticalLayout.addWidget(self.box)
        self.retranslateUi(ShotgunFolderWidget)
        QMetaObject.connectSlotsByName(ShotgunFolderWidget)
    # setupUi
    def retranslateUi(self, ShotgunFolderWidget):
        ShotgunFolderWidget.setWindowTitle(QCoreApplication.translate("ShotgunFolderWidget", u"Form", None))
        self.thumbnail.setText("")
        self.header.setText(QCoreApplication.translate("ShotgunFolderWidget", u"header", None))
        self.button.setText(QCoreApplication.translate("ShotgunFolderWidget", u"Actions", None))
        self.body.setText(QCoreApplication.translate("ShotgunFolderWidget", u"body", None))
    # retranslateUi
