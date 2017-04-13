# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reply_dialog.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ReplyDialog(object):
    def setupUi(self, ReplyDialog):
        ReplyDialog.setObjectName("ReplyDialog")
        ReplyDialog.resize(416, 128)
        ReplyDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(ReplyDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(ReplyDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.note_widget = NoteInputWidget(ReplyDialog)
        self.note_widget.setMinimumSize(QtCore.QSize(0, 40))
        self.note_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.note_widget.setObjectName("note_widget")
        self.verticalLayout.addWidget(self.note_widget)

        self.retranslateUi(ReplyDialog)
        QtCore.QMetaObject.connectSlotsByName(ReplyDialog)

    def retranslateUi(self, ReplyDialog):
        ReplyDialog.setWindowTitle(QtGui.QApplication.translate("ReplyDialog", "Reply", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ReplyDialog", "<big>Please enter a Reply:</big>", None, QtGui.QApplication.UnicodeUTF8))

from ..qtwidgets import NoteInputWidget
