# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'breadcrumb_widget.ui'
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


from ..qtwidgets import ElidedLabel

class Ui_BreadcrumbWidget(object):
    def setupUi(self, BreadcrumbWidget):
        if not BreadcrumbWidget.objectName():
            BreadcrumbWidget.setObjectName(u"BreadcrumbWidget")
        BreadcrumbWidget.resize(227, 16)
        self.horizontalLayout = QHBoxLayout(BreadcrumbWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.path_label = ElidedLabel(BreadcrumbWidget)
        self.path_label.setObjectName(u"path_label")
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.path_label.sizePolicy().hasHeightForWidth())
        self.path_label.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.path_label)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.retranslateUi(BreadcrumbWidget)

        QMetaObject.connectSlotsByName(BreadcrumbWidget)
    # setupUi

    def retranslateUi(self, BreadcrumbWidget):
        BreadcrumbWidget.setWindowTitle(QCoreApplication.translate("BreadcrumbWidget", u"Form", None))
        self.path_label.setText(QCoreApplication.translate("BreadcrumbWidget", u"I <span style='color:#2C93E2'>&#9656;</span> Am <span style='color:#2C93E2'>&#9656;</span> Groot", None))
    # retranslateUi
