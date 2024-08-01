# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'collapse_widget.ui'
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

class Ui_CollapseWidget(object):
    def setupUi(self, CollapseWidget):
        if not CollapseWidget.objectName():
            CollapseWidget.setObjectName(u"CollapseWidget")
        CollapseWidget.resize(332, 16)
        self.verticalLayout = QVBoxLayout(CollapseWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(CollapseWidget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(CollapseWidget)

        QMetaObject.connectSlotsByName(CollapseWidget)
    # setupUi

    def retranslateUi(self, CollapseWidget):
        CollapseWidget.setWindowTitle(QCoreApplication.translate("CollapseWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("CollapseWidget", u"<i><small>Hiding 8 notes...</small></i>", None))
    # retranslateUi
