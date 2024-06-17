# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'dialog.ui'
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
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(784, 483)
        Dialog.setStyleSheet(u"#Dialog {\n"
"background-image: url(:/tk_framework_qtwidgets.help_screen/bg.png);\n"
"}\n"
"\n"
"")
        self.horizontalLayout_2 = QHBoxLayout(Dialog)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(34, 0))
        self.label.setMaximumSize(QSize(34, 16777215))
        self.verticalLayout_3.addWidget(self.label)
        self.left_arrow = QToolButton(Dialog)
        self.left_arrow.setObjectName(u"left_arrow")
        self.left_arrow.setMinimumSize(QSize(34, 34))
        self.left_arrow.setFocusPolicy(Qt.ClickFocus)
        self.left_arrow.setStyleSheet(u"QToolButton{\n"
"background-image: url(:/tk_framework_qtwidgets.help_screen/left_arrow.png);\n"
"border: none;\n"
"background-color: none;\n"
"}\n"
"\n"
"\n"
"QToolButton:hover{\n"
"background-image: url(:/tk_framework_qtwidgets.help_screen/left_arrow_hover.png);\n"
"}\n"
"\n"
"QToolButton:Pressed {\n"
"background-image: url(:/tk_framework_qtwidgets.help_screen/left_arrow_pressed.png);\n"
"}\n"
"")
        self.left_arrow.setAutoRaise(True)
        self.verticalLayout_3.addWidget(self.left_arrow)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(34, 0))
        self.label_2.setMaximumSize(QSize(34, 16777215))
        self.verticalLayout_3.addWidget(self.label_2)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"#groupBox {\n"
"background-color: rgba(0,0,0,50);\n"
"\n"
"}")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget = QStackedWidget(self.groupBox)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.verticalLayout.addWidget(self.stackedWidget)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(248, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        self.view_documentation = QToolButton(Dialog)
        self.view_documentation.setObjectName(u"view_documentation")
        self.horizontalLayout.addWidget(self.view_documentation)
        self.close = QToolButton(Dialog)
        self.close.setObjectName(u"close")
        self.horizontalLayout.addWidget(self.close)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(34, 0))
        self.label_3.setMaximumSize(QSize(34, 16777215))
        self.verticalLayout_4.addWidget(self.label_3)
        self.right_arrow = QToolButton(Dialog)
        self.right_arrow.setObjectName(u"right_arrow")
        self.right_arrow.setMinimumSize(QSize(34, 34))
        self.right_arrow.setFocusPolicy(Qt.ClickFocus)
        self.right_arrow.setStyleSheet(u"QToolButton{\n"
"background-image: url(:/tk_framework_qtwidgets.help_screen/right_arrow.png);\n"
"border: none;\n"
"background-color: none;\n"
"}\n"
"\n"
"\n"
"QToolButton:hover{\n"
"background-image: url(:/tk_framework_qtwidgets.help_screen/right_arrow_hover.png);\n"
"}\n"
"\n"
"QToolButton:Pressed {\n"
"background-image: url(:/tk_framework_qtwidgets.help_screen/right_arrow_pressed.png);\n"
"}\n"
"")
        self.right_arrow.setAutoRaise(True)
        self.verticalLayout_4.addWidget(self.right_arrow)
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(34, 0))
        self.label_4.setMaximumSize(QSize(34, 16777215))
        self.verticalLayout_4.addWidget(self.label_4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(-1)
        QMetaObject.connectSlotsByName(Dialog)
    # setupUi
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Form", None))
        self.label.setText("")
#if QT_CONFIG(tooltip)
        self.left_arrow.setToolTip(QCoreApplication.translate("Dialog", u"Scroll to the previous slide", None))
#endif // QT_CONFIG(tooltip)
        self.left_arrow.setText("")
        self.label_2.setText("")
        self.groupBox.setTitle("")
        self.view_documentation.setText(QCoreApplication.translate("Dialog", u"Jump to Documentation", None))
        self.close.setText(QCoreApplication.translate("Dialog", u"Close", None))
        self.label_3.setText("")
#if QT_CONFIG(tooltip)
        self.right_arrow.setToolTip(QCoreApplication.translate("Dialog", u"Scroll to the next slide", None))
#endif // QT_CONFIG(tooltip)
        self.right_arrow.setText("")
        self.label_4.setText("")
    # retranslateUi
