# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'attachment_group_widget.ui'
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
from  . import resources_rc
class Ui_AttachmentGroupWidget(object):
    def setupUi(self, AttachmentGroupWidget):
        if not AttachmentGroupWidget.objectName():
            AttachmentGroupWidget.setObjectName(u"AttachmentGroupWidget")
        AttachmentGroupWidget.resize(577, 182)
        self.verticalLayout = QVBoxLayout(AttachmentGroupWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(36, 6, 0, 0)
        self.attachments_label = QLabel(AttachmentGroupWidget)
        self.attachments_label.setObjectName(u"attachments_label")
        self.attachments_label.setMinimumSize(QSize(100, 16))
        self.attachments_label.setMaximumSize(QSize(100, 16))
        self.attachments_label.setPixmap(QPixmap(u":/tk_framework_qtwidgets.activity_stream/attachments.png"))
        self.attachments_label.setScaledContents(True)
        self.verticalLayout.addWidget(self.attachments_label)
        self.preview_frame = QFrame(AttachmentGroupWidget)
        self.preview_frame.setObjectName(u"preview_frame")
        self.preview_frame.setFrameShape(QFrame.NoFrame)
        self.preview_frame.setFrameShadow(QFrame.Raised)
        self.preview_layout = QGridLayout(self.preview_frame)
        self.preview_layout.setSpacing(2)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setObjectName(u"preview_layout")
        self.verticalLayout.addWidget(self.preview_frame)
        self.attachment_frame = QFrame(AttachmentGroupWidget)
        self.attachment_frame.setObjectName(u"attachment_frame")
        self.attachment_frame.setFrameShape(QFrame.NoFrame)
        self.attachment_frame.setFrameShadow(QFrame.Raised)
        self.attachment_layout = QVBoxLayout(self.attachment_frame)
        self.attachment_layout.setContentsMargins(2, 2, 2, 2)
        self.attachment_layout.setObjectName(u"attachment_layout")
        self.verticalLayout.addWidget(self.attachment_frame)
        self.retranslateUi(AttachmentGroupWidget)
        QMetaObject.connectSlotsByName(AttachmentGroupWidget)
    # setupUi
    def retranslateUi(self, AttachmentGroupWidget):
        AttachmentGroupWidget.setWindowTitle(QCoreApplication.translate("AttachmentGroupWidget", u"Form", None))
        self.attachments_label.setText("")
    # retranslateUi
