# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'thumbnail_widget.ui'
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


from  . import resources_rc

class Ui_ThumbnailWidget(object):
    def setupUi(self, ThumbnailWidget):
        if not ThumbnailWidget.objectName():
            ThumbnailWidget.setObjectName(u"ThumbnailWidget")
        ThumbnailWidget.resize(347, 266)
        ThumbnailWidget.setStyleSheet(u"")
        self.thumbnail = QLabel(ThumbnailWidget)
        self.thumbnail.setObjectName(u"thumbnail")
        self.thumbnail.setGeometry(QRect(210, 190, 81, 61))
        self.thumbnail.setMinimumSize(QSize(0, 0))
        self.thumbnail.setMaximumSize(QSize(16777215, 16777215))
        self.thumbnail.setStyleSheet(u"")
        self.thumbnail.setScaledContents(False)
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.buttons_frame = QFrame(ThumbnailWidget)
        self.buttons_frame.setObjectName(u"buttons_frame")
        self.buttons_frame.setGeometry(QRect(40, 30, 211, 191))
        self.buttons_frame.setStyleSheet(u"#buttons_frame {\n"
"border-radius: 2px;\n"
"background-color: rgba(0,0,0, 64);\n"
"}")
        self.buttons_frame.setFrameShape(QFrame.NoFrame)
        self.buttons_frame.setFrameShadow(QFrame.Plain)
        self.buttons_frame.setLineWidth(0)
        self.verticalLayout_2 = QVBoxLayout(self.buttons_frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_2 = QSpacerItem(20, 52, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.camera_btn = QPushButton(self.buttons_frame)
        self.camera_btn.setObjectName(u"camera_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_btn.sizePolicy().hasHeightForWidth())
        self.camera_btn.setSizePolicy(sizePolicy)
        self.camera_btn.setMinimumSize(QSize(64, 64))
        self.camera_btn.setMaximumSize(QSize(16777215, 16777215))
        self.camera_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.camera_btn.setStyleSheet(u"#camera_btn {\n"
"    background-color: rgba( 0, 0, 0, 0 );\n"
"	image: url(:/tk_framework_qtwidgets.thumbnail_widget/camera.png);\n"
"	margin: 5px;\n"
"	border: none;\n"
"}\n"
"#camera_btn:hover {\n"
"	image: url(:/tk_framework_qtwidgets.thumbnail_widget/camera_hl.png);\n"
"}\n"
"#camera_btn:focus:pressed {\n"
"	image: url(:/tk_framework_qtwidgets.thumbnail_widget/camera_hl.png);\n"
"}\n"
"\n"
"")
        self.camera_btn.setIconSize(QSize(64, 64))
        self.camera_btn.setFlat(True)

        self.horizontalLayout_2.addWidget(self.camera_btn)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 2)
        self.horizontalLayout_2.setStretch(2, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 51, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 2)
        self.verticalLayout_2.setStretch(2, 1)

        self.retranslateUi(ThumbnailWidget)

        QMetaObject.connectSlotsByName(ThumbnailWidget)
    # setupUi

    def retranslateUi(self, ThumbnailWidget):
        ThumbnailWidget.setWindowTitle(QCoreApplication.translate("ThumbnailWidget", u"Form", None))
        self.thumbnail.setText("")
        self.camera_btn.setText("")
    # retranslateUi
