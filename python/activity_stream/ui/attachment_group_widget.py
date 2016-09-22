# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'attachment_group_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_AttachmentGroupWidget(object):
    def setupUi(self, AttachmentGroupWidget):
        AttachmentGroupWidget.setObjectName("AttachmentGroupWidget")
        AttachmentGroupWidget.resize(577, 182)
        self.verticalLayout = QtGui.QVBoxLayout(AttachmentGroupWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(36, 6, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.attachments_label = QtGui.QLabel(AttachmentGroupWidget)
        self.attachments_label.setMinimumSize(QtCore.QSize(100, 16))
        self.attachments_label.setMaximumSize(QtCore.QSize(100, 16))
        self.attachments_label.setText("")
        self.attachments_label.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/attachments.png"))
        self.attachments_label.setScaledContents(True)
        self.attachments_label.setObjectName("attachments_label")
        self.verticalLayout.addWidget(self.attachments_label)
        self.preview_frame = QtGui.QFrame(AttachmentGroupWidget)
        self.preview_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.preview_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.preview_frame.setObjectName("preview_frame")
        self.preview_layout = QtGui.QGridLayout(self.preview_frame)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(2)
        self.preview_layout.setObjectName("preview_layout")
        self.verticalLayout.addWidget(self.preview_frame)
        self.attachment_frame = QtGui.QFrame(AttachmentGroupWidget)
        self.attachment_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.attachment_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.attachment_frame.setObjectName("attachment_frame")
        self.attachment_layout = QtGui.QVBoxLayout(self.attachment_frame)
        self.attachment_layout.setContentsMargins(2, 2, 2, 2)
        self.attachment_layout.setObjectName("attachment_layout")
        self.verticalLayout.addWidget(self.attachment_frame)

        self.retranslateUi(AttachmentGroupWidget)
        QtCore.QMetaObject.connectSlotsByName(AttachmentGroupWidget)

    def retranslateUi(self, AttachmentGroupWidget):
        AttachmentGroupWidget.setWindowTitle(QtGui.QApplication.translate("AttachmentGroupWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
from . import resources_rc
