# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shotgun_folder_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

class Ui_ShotgunFolderWidget(object):
    def setupUi(self, ShotgunFolderWidget):
        ShotgunFolderWidget.setObjectName("ShotgunFolderWidget")
        ShotgunFolderWidget.resize(564, 512)
        self.verticalLayout = QtGui.QVBoxLayout(ShotgunFolderWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.box = QtGui.QFrame(ShotgunFolderWidget)
        self.box.setFrameShape(QtGui.QFrame.StyledPanel)
        self.box.setFrameShadow(QtGui.QFrame.Raised)
        self.box.setObjectName("box")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.box)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.thumbnail_layout = QtGui.QHBoxLayout()
        self.thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        self.thumbnail_layout.setObjectName("thumbnail_layout")
        self.thumbnail = QtGui.QLabel(self.box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thumbnail.sizePolicy().hasHeightForWidth())
        self.thumbnail.setSizePolicy(sizePolicy)
        self.thumbnail.setMinimumSize(QtCore.QSize(0, 0))
        self.thumbnail.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.thumbnail.setText("")
        self.thumbnail.setPixmap(QtGui.QPixmap(":/tk-framework-qtwidgets/shotgun_widget/rect_512x400.png"))
        self.thumbnail.setScaledContents(False)
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail.setObjectName("thumbnail")
        self.thumbnail_layout.addWidget(self.thumbnail)
        self.verticalLayout_2.addLayout(self.thumbnail_layout)
        self.header_layout = QtGui.QHBoxLayout()
        self.header_layout.setContentsMargins(-1, 0, -1, -1)
        self.header_layout.setObjectName("header_layout")
        self.header = QtGui.QLabel(self.box)
        self.header.setObjectName("header")
        self.header_layout.addWidget(self.header)
        self.button = QtGui.QToolButton(self.box)
        self.button.setObjectName("button")
        self.header_layout.addWidget(self.button)
        self.verticalLayout_2.addLayout(self.header_layout)
        self.body = QtGui.QLabel(self.box)
        self.body.setObjectName("body")
        self.verticalLayout_2.addWidget(self.body)
        self.verticalLayout.addWidget(self.box)

        self.retranslateUi(ShotgunFolderWidget)
        QtCore.QMetaObject.connectSlotsByName(ShotgunFolderWidget)

    def retranslateUi(self, ShotgunFolderWidget):
        ShotgunFolderWidget.setWindowTitle(QtGui.QApplication.translate("ShotgunFolderWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("ShotgunFolderWidget", "header", None, QtGui.QApplication.UnicodeUTF8))
        self.button.setText(QtGui.QApplication.translate("ShotgunFolderWidget", "Actions", None, QtGui.QApplication.UnicodeUTF8))
        self.body.setText(QtGui.QApplication.translate("ShotgunFolderWidget", "body", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
