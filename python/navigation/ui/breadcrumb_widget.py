# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'breadcrumb_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_BreadcrumbWidget(object):
    def setupUi(self, BreadcrumbWidget):
        BreadcrumbWidget.setObjectName("BreadcrumbWidget")
        BreadcrumbWidget.resize(227, 16)
        self.horizontalLayout = QtGui.QHBoxLayout(BreadcrumbWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.path_label = ElidedLabel(BreadcrumbWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.path_label.sizePolicy().hasHeightForWidth())
        self.path_label.setSizePolicy(sizePolicy)
        self.path_label.setObjectName("path_label")
        self.horizontalLayout.addWidget(self.path_label)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(BreadcrumbWidget)
        QtCore.QMetaObject.connectSlotsByName(BreadcrumbWidget)

    def retranslateUi(self, BreadcrumbWidget):
        BreadcrumbWidget.setWindowTitle(QtGui.QApplication.translate("BreadcrumbWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.path_label.setText(QtGui.QApplication.translate("BreadcrumbWidget", "I <span style=\'color:#2C93E2\'>&#9656;</span> Am <span style=\'color:#2C93E2\'>&#9656;</span> Groot", None, QtGui.QApplication.UnicodeUTF8))

from ..qtwidgets import ElidedLabel
