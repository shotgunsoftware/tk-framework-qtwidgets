# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'header.ui'
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


class Ui_Header(object):
    def setupUi(self, Header):
        if not Header.objectName():
            Header.setObjectName(u"Header")
        Header.resize(389, 37)
        Header.setMinimumSize(QSize(0, 0))
        Header.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(Header)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 12, 3, 3)
        self.label = QLabel(Header)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"")
        self.label.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.verticalLayout.addWidget(self.label)

        self.line = QFrame(Header)
        self.line.setObjectName(u"line")
        self.line.setStyleSheet(u"")
        self.line.setFrameShadow(QFrame.Plain)
        self.line.setFrameShape(QFrame.HLine)

        self.verticalLayout.addWidget(self.line)

        self.retranslateUi(Header)

        QMetaObject.connectSlotsByName(Header)
    # setupUi

    def retranslateUi(self, Header):
        Header.setWindowTitle(QCoreApplication.translate("Header", u"Form", None))
        self.label.setText(QCoreApplication.translate("Header", u"<big>Header</big>", None))
    # retranslateUi
