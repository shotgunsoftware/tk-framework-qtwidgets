# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'reply_dialog.ui'
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

from ..qtwidgets import NoteInputWidget
class Ui_ReplyDialog(object):
    def setupUi(self, ReplyDialog):
        if not ReplyDialog.objectName():
            ReplyDialog.setObjectName(u"ReplyDialog")
        ReplyDialog.resize(416, 128)
        ReplyDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(ReplyDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(ReplyDialog)
        self.label.setObjectName(u"label")
        self.verticalLayout.addWidget(self.label)
        self.note_widget = NoteInputWidget(ReplyDialog)
        self.note_widget.setObjectName(u"note_widget")
        self.note_widget.setMinimumSize(QSize(0, 40))
        self.note_widget.setFocusPolicy(Qt.NoFocus)
        self.verticalLayout.addWidget(self.note_widget)
        self.retranslateUi(ReplyDialog)
        QMetaObject.connectSlotsByName(ReplyDialog)
    # setupUi
    def retranslateUi(self, ReplyDialog):
        ReplyDialog.setWindowTitle(QCoreApplication.translate("ReplyDialog", u"Reply", None))
        self.label.setText(QCoreApplication.translate("ReplyDialog", u"<big>Please enter a Reply:</big>", None))
    # retranslateUi
