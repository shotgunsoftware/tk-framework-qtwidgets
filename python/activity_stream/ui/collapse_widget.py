# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'collapse_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_CollapseWidget(object):
    def setupUi(self, CollapseWidget):
        CollapseWidget.setObjectName("CollapseWidget")
        CollapseWidget.resize(332, 16)
        self.verticalLayout = QtGui.QVBoxLayout(CollapseWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(CollapseWidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(CollapseWidget)
        QtCore.QMetaObject.connectSlotsByName(CollapseWidget)

    def retranslateUi(self, CollapseWidget):
        CollapseWidget.setWindowTitle(QtGui.QApplication.translate("CollapseWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CollapseWidget", "<i><small>Hiding 8 notes...</small></i>", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
