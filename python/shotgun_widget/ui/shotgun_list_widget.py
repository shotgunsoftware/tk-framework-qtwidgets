# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shotgun_list_widget.ui'
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

class Ui_ShotgunListWidget(object):
    def setupUi(self, ShotgunListWidget):
        if not ShotgunListWidget.objectName():
            ShotgunListWidget.setObjectName(u"ShotgunListWidget")
        ShotgunListWidget.resize(355, 105)
        self.horizontalLayout = QHBoxLayout(ShotgunListWidget)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 4, 8, 4)
        self.box = QFrame(ShotgunListWidget)
        self.box.setObjectName(u"box")
        self.box.setFrameShape(QFrame.StyledPanel)
        self.box.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(4, 8, 4, 8)
        self.thumbnail = QLabel(self.box)
        self.thumbnail.setObjectName(u"thumbnail")
        self.thumbnail.setMinimumSize(QSize(96, 75))
        self.thumbnail.setMaximumSize(QSize(96, 75))
        self.thumbnail.setPixmap(QPixmap(u":/tk-framework-qtwidgets/shotgun_widget/rect_512x400.png"))
        self.thumbnail.setScaledContents(False)
        self.thumbnail.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.thumbnail)

        self.data_layout = QVBoxLayout()
        self.data_layout.setSpacing(3)
        self.data_layout.setObjectName(u"data_layout")
        self.corner_layout = QHBoxLayout()
        self.corner_layout.setSpacing(5)
        self.corner_layout.setObjectName(u"corner_layout")
        self.left_corner = QLabel(self.box)
        self.left_corner.setObjectName(u"left_corner")

        self.corner_layout.addWidget(self.left_corner)

        self.right_corner = QLabel(self.box)
        self.right_corner.setObjectName(u"right_corner")
        self.right_corner.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.corner_layout.addWidget(self.right_corner)

        self.button = QToolButton(self.box)
        self.button.setObjectName(u"button")
        self.button.setPopupMode(QToolButton.InstantPopup)
        self.button.setToolButtonStyle(Qt.ToolButtonTextOnly)

        self.corner_layout.addWidget(self.button)

        self.data_layout.addLayout(self.corner_layout)

        self.body = QLabel(self.box)
        self.body.setObjectName(u"body")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.body.sizePolicy().hasHeightForWidth())
        self.body.setSizePolicy(sizePolicy)
        self.body.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.data_layout.addWidget(self.body)

        self.horizontalLayout_2.addLayout(self.data_layout)

        self.horizontalLayout.addWidget(self.box)

        self.retranslateUi(ShotgunListWidget)

        QMetaObject.connectSlotsByName(ShotgunListWidget)
    # setupUi

    def retranslateUi(self, ShotgunListWidget):
        ShotgunListWidget.setWindowTitle(QCoreApplication.translate("ShotgunListWidget", u"Form", None))
        self.thumbnail.setText("")
        self.left_corner.setText(QCoreApplication.translate("ShotgunListWidget", u"left corner", None))
        self.right_corner.setText(QCoreApplication.translate("ShotgunListWidget", u"right corner", None))
        self.button.setText(QCoreApplication.translate("ShotgunListWidget", u"Actions", None))
        self.body.setText(QCoreApplication.translate("ShotgunListWidget", u"body text", None))
    # retranslateUi
