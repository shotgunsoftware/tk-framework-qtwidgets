# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_item_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_NewItemWidget(object):
    def setupUi(self, NewItemWidget):
        NewItemWidget.setObjectName("NewItemWidget")
        NewItemWidget.resize(342, 222)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(NewItemWidget)
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.user_thumb = UserThumbnail(NewItemWidget)
        self.user_thumb.setMinimumSize(QtCore.QSize(50, 50))
        self.user_thumb.setMaximumSize(QtCore.QSize(50, 50))
        self.user_thumb.setText("")
        self.user_thumb.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.user_thumb.setObjectName("user_thumb")
        self.verticalLayout_2.addWidget(self.user_thumb)
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.frame = QtGui.QFrame(NewItemWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.header_left = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_left.sizePolicy().hasHeightForWidth())
        self.header_left.setSizePolicy(sizePolicy)
        self.header_left.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.header_left.setWordWrap(True)
        self.header_left.setObjectName("header_left")
        self.horizontalLayout.addWidget(self.header_left)
        self.date = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        self.date.setSizePolicy(sizePolicy)
        self.date.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.date.setWordWrap(True)
        self.date.setObjectName("date")
        self.horizontalLayout.addWidget(self.date)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.details_thumb = ShotgunPlaybackLabel(self.frame)
        self.details_thumb.setMinimumSize(QtCore.QSize(256, 144))
        self.details_thumb.setMaximumSize(QtCore.QSize(256, 144))
        self.details_thumb.setText("")
        self.details_thumb.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/rect_256x144.png"))
        self.details_thumb.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.details_thumb.setObjectName("details_thumb")
        self.verticalLayout.addWidget(self.details_thumb)
        self.footer = QtGui.QLabel(self.frame)
        self.footer.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.footer.setWordWrap(True)
        self.footer.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.footer.setObjectName("footer")
        self.verticalLayout.addWidget(self.footer)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(NewItemWidget)
        QtCore.QMetaObject.connectSlotsByName(NewItemWidget)

    def retranslateUi(self, NewItemWidget):
        NewItemWidget.setWindowTitle(QtGui.QApplication.translate("NewItemWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header_left.setText(QtGui.QApplication.translate("NewItemWidget", "John Smith", None, QtGui.QApplication.UnicodeUTF8))
        self.date.setText(QtGui.QApplication.translate("NewItemWidget", "3 days ago", None, QtGui.QApplication.UnicodeUTF8))
        self.footer.setText(QtGui.QApplication.translate("NewItemWidget", "description", None, QtGui.QApplication.UnicodeUTF8))

from ..qtwidgets import ShotgunPlaybackLabel
from ..label_widgets import UserThumbnail
from . import resources_rc
