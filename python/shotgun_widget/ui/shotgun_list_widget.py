# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shotgun_list_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

class Ui_ShotgunListWidget(object):
    def setupUi(self, ShotgunListWidget):
        ShotgunListWidget.setObjectName("ShotgunListWidget")
        ShotgunListWidget.resize(355, 105)
        self.horizontalLayout = QtGui.QHBoxLayout(ShotgunListWidget)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setContentsMargins(8, 4, 8, 4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.box = QtGui.QFrame(ShotgunListWidget)
        self.box.setFrameShape(QtGui.QFrame.StyledPanel)
        self.box.setFrameShadow(QtGui.QFrame.Raised)
        self.box.setObjectName("box")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setContentsMargins(4, 8, 4, 8)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.thumbnail = QtGui.QLabel(self.box)
        self.thumbnail.setMinimumSize(QtCore.QSize(96, 75))
        self.thumbnail.setMaximumSize(QtCore.QSize(96, 75))
        self.thumbnail.setText("")
        self.thumbnail.setPixmap(QtGui.QPixmap(":/tk-framework-qtwidgets/shotgun_widget/rect_512x400.png"))
        self.thumbnail.setScaledContents(False)
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail.setObjectName("thumbnail")
        self.horizontalLayout_2.addWidget(self.thumbnail)
        self.data_layout = QtGui.QVBoxLayout()
        self.data_layout.setSpacing(3)
        self.data_layout.setObjectName("data_layout")
        self.corner_layout = QtGui.QHBoxLayout()
        self.corner_layout.setSpacing(5)
        self.corner_layout.setObjectName("corner_layout")
        self.left_corner = QtGui.QLabel(self.box)
        self.left_corner.setObjectName("left_corner")
        self.corner_layout.addWidget(self.left_corner)
        self.right_corner = QtGui.QLabel(self.box)
        self.right_corner.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.right_corner.setObjectName("right_corner")
        self.corner_layout.addWidget(self.right_corner)
        self.button = QtGui.QToolButton(self.box)
        self.button.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.button.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.button.setObjectName("button")
        self.corner_layout.addWidget(self.button)
        self.data_layout.addLayout(self.corner_layout)
        self.body = QtGui.QLabel(self.box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.body.sizePolicy().hasHeightForWidth())
        self.body.setSizePolicy(sizePolicy)
        self.body.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.body.setObjectName("body")
        self.data_layout.addWidget(self.body)
        self.horizontalLayout_2.addLayout(self.data_layout)
        self.horizontalLayout.addWidget(self.box)

        self.retranslateUi(ShotgunListWidget)
        QtCore.QMetaObject.connectSlotsByName(ShotgunListWidget)

    def retranslateUi(self, ShotgunListWidget):
        ShotgunListWidget.setWindowTitle(QtGui.QApplication.translate("ShotgunListWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.left_corner.setText(QtGui.QApplication.translate("ShotgunListWidget", "left corner", None, QtGui.QApplication.UnicodeUTF8))
        self.right_corner.setText(QtGui.QApplication.translate("ShotgunListWidget", "right corner", None, QtGui.QApplication.UnicodeUTF8))
        self.button.setText(QtGui.QApplication.translate("ShotgunListWidget", "Actions", None, QtGui.QApplication.UnicodeUTF8))
        self.body.setText(QtGui.QApplication.translate("ShotgunListWidget", "body text", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
