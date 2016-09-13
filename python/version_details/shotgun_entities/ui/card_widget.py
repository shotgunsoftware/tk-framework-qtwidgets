# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'card_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ShotgunEntityCardWidget(object):
    def setupUi(self, ShotgunEntityCardWidget):
        ShotgunEntityCardWidget.setObjectName("ShotgunEntityCardWidget")
        ShotgunEntityCardWidget.resize(355, 75)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ShotgunEntityCardWidget.sizePolicy().hasHeightForWidth())
        ShotgunEntityCardWidget.setSizePolicy(sizePolicy)
        ShotgunEntityCardWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(ShotgunEntityCardWidget)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.box = QtGui.QFrame(ShotgunEntityCardWidget)
        self.box.setFrameShape(QtGui.QFrame.NoFrame)
        self.box.setFrameShadow(QtGui.QFrame.Plain)
        self.box.setObjectName("box")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.box_layout = QtGui.QHBoxLayout()
        self.box_layout.setSpacing(10)
        self.box_layout.setContentsMargins(0, -1, -1, -1)
        self.box_layout.setObjectName("box_layout")
        self.left_layout = QtGui.QVBoxLayout()
        self.left_layout.setObjectName("left_layout")
        self.box_layout.addLayout(self.left_layout)
        self.right_layout = QtGui.QVBoxLayout()
        self.right_layout.setSpacing(0)
        self.right_layout.setContentsMargins(-1, 0, -1, 0)
        self.right_layout.setObjectName("right_layout")
        self.field_grid_layout = QtGui.QGridLayout()
        self.field_grid_layout.setContentsMargins(-1, 4, -1, 4)
        self.field_grid_layout.setHorizontalSpacing(5)
        self.field_grid_layout.setVerticalSpacing(2)
        self.field_grid_layout.setObjectName("field_grid_layout")
        self.right_layout.addLayout(self.field_grid_layout)
        self.box_layout.addLayout(self.right_layout)
        self.horizontalLayout_2.addLayout(self.box_layout)
        self.horizontalLayout_3.addWidget(self.box)

        self.retranslateUi(ShotgunEntityCardWidget)
        QtCore.QMetaObject.connectSlotsByName(ShotgunEntityCardWidget)

    def retranslateUi(self, ShotgunEntityCardWidget):
        ShotgunEntityCardWidget.setWindowTitle(QtGui.QApplication.translate("ShotgunEntityCardWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

