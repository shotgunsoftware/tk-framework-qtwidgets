# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'card_widget.ui'
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

class Ui_ShotgunEntityCardWidget(object):
    def setupUi(self, ShotgunEntityCardWidget):
        if not ShotgunEntityCardWidget.objectName():
            ShotgunEntityCardWidget.setObjectName(u"ShotgunEntityCardWidget")
        ShotgunEntityCardWidget.resize(355, 75)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ShotgunEntityCardWidget.sizePolicy().hasHeightForWidth())
        ShotgunEntityCardWidget.setSizePolicy(sizePolicy)
        ShotgunEntityCardWidget.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_3 = QHBoxLayout(ShotgunEntityCardWidget)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.box = QFrame(ShotgunEntityCardWidget)
        self.box.setObjectName(u"box")
        self.box.setFrameShape(QFrame.NoFrame)
        self.box.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_2 = QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.box_layout = QHBoxLayout()
        self.box_layout.setSpacing(10)
        self.box_layout.setObjectName(u"box_layout")
        self.box_layout.setContentsMargins(0, -1, -1, -1)
        self.left_layout = QVBoxLayout()
        self.left_layout.setObjectName(u"left_layout")
        self.box_layout.addLayout(self.left_layout)
        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(0)
        self.right_layout.setObjectName(u"right_layout")
        self.right_layout.setContentsMargins(-1, 0, -1, 0)
        self.field_grid_layout = QGridLayout()
        self.field_grid_layout.setObjectName(u"field_grid_layout")
        self.field_grid_layout.setHorizontalSpacing(5)
        self.field_grid_layout.setVerticalSpacing(2)
        self.field_grid_layout.setContentsMargins(-1, 4, -1, 4)
        self.right_layout.addLayout(self.field_grid_layout)
        self.box_layout.addLayout(self.right_layout)
        self.horizontalLayout_2.addLayout(self.box_layout)
        self.horizontalLayout_3.addWidget(self.box)
        self.retranslateUi(ShotgunEntityCardWidget)
        QMetaObject.connectSlotsByName(ShotgunEntityCardWidget)
    # setupUi
    def retranslateUi(self, ShotgunEntityCardWidget):
        ShotgunEntityCardWidget.setWindowTitle(QCoreApplication.translate("ShotgunEntityCardWidget", u"Form", None))
    # retranslateUi
