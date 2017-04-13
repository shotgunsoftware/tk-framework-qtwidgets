# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'navigation_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_NavigationWidget(object):
    def setupUi(self, NavigationWidget):
        NavigationWidget.setObjectName("NavigationWidget")
        NavigationWidget.resize(119, 38)
        self.horizontalLayout = QtGui.QHBoxLayout(NavigationWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nav_home_btn = QtGui.QToolButton(NavigationWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nav_home_btn.sizePolicy().hasHeightForWidth())
        self.nav_home_btn.setSizePolicy(sizePolicy)
        self.nav_home_btn.setMinimumSize(QtCore.QSize(39, 36))
        self.nav_home_btn.setMaximumSize(QtCore.QSize(39, 36))
        self.nav_home_btn.setBaseSize(QtCore.QSize(0, 0))
        self.nav_home_btn.setStyleSheet("#nav_home_btn{\n"
"   border: none;\n"
"   background-color: none;\n"
"   background-repeat: no-repeat;\n"
"   background-position: center center;\n"
"   background-image: url(:/tk-multi-workfiles2/home.png);\n"
"}\n"
"\n"
"#nav_home_btn:disabled{\n"
"   background-image: url(:/tk-multi-workfiles2/home_disabled.png);\n"
"}\n"
"\n"
"#nav_home_btn:hover{\n"
"background-image: url(:/tk-multi-workfiles2/home_hover.png);\n"
"}\n"
"\n"
"#nav_home_btn:Pressed {\n"
"background-image: url(:/tk-multi-workfiles2/home_pressed.png);\n"
"}\n"
"")
        self.nav_home_btn.setText("")
        self.nav_home_btn.setObjectName("nav_home_btn")
        self.horizontalLayout_2.addWidget(self.nav_home_btn)
        self.nav_prev_btn = QtGui.QToolButton(NavigationWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nav_prev_btn.sizePolicy().hasHeightForWidth())
        self.nav_prev_btn.setSizePolicy(sizePolicy)
        self.nav_prev_btn.setMinimumSize(QtCore.QSize(34, 36))
        self.nav_prev_btn.setMaximumSize(QtCore.QSize(34, 36))
        self.nav_prev_btn.setBaseSize(QtCore.QSize(0, 0))
        self.nav_prev_btn.setStyleSheet("#nav_prev_btn{\n"
"   border: none;\n"
"   background-color: none;\n"
"   background-repeat: no-repeat;\n"
"   background-position: center center;\n"
"   background-image: url(:/tk-multi-workfiles2/left_arrow.png);\n"
"}\n"
"\n"
"#nav_prev_btn:disabled{\n"
"   background-image: url(:/tk-multi-workfiles2/left_arrow_disabled.png);\n"
"}\n"
"\n"
"#nav_prev_btn:hover{\n"
"background-image: url(:/tk-multi-workfiles2/left_arrow_hover.png);\n"
"}\n"
"\n"
"#nav_prev_btn:Pressed {\n"
"background-image: url(:/tk-multi-workfiles2/left_arrow_pressed.png);\n"
"}\n"
"")
        self.nav_prev_btn.setText("")
        self.nav_prev_btn.setObjectName("nav_prev_btn")
        self.horizontalLayout_2.addWidget(self.nav_prev_btn)
        self.nav_next_btn = QtGui.QToolButton(NavigationWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nav_next_btn.sizePolicy().hasHeightForWidth())
        self.nav_next_btn.setSizePolicy(sizePolicy)
        self.nav_next_btn.setMinimumSize(QtCore.QSize(34, 36))
        self.nav_next_btn.setMaximumSize(QtCore.QSize(34, 36))
        self.nav_next_btn.setBaseSize(QtCore.QSize(0, 0))
        self.nav_next_btn.setStyleSheet("#nav_next_btn{\n"
"   border: none;\n"
"   background-color: none;\n"
"   background-repeat: no-repeat;\n"
"   background-position: center center;\n"
"   background-image: url(:/tk-multi-workfiles2/right_arrow.png);\n"
"}\n"
"\n"
"#nav_next_btn:disabled{\n"
"   background-image: url(:/tk-multi-workfiles2/right_arrow_disabled.png);\n"
"}\n"
"\n"
"#nav_next_btn:hover{\n"
"background-image: url(:/tk-multi-workfiles2/right_arrow_hover.png);\n"
"}\n"
"\n"
"#nav_next_btn:Pressed {\n"
"background-image: url(:/tk-multi-workfiles2/right_arrow_pressed.png);\n"
"}\n"
"")
        self.nav_next_btn.setText("")
        self.nav_next_btn.setObjectName("nav_next_btn")
        self.horizontalLayout_2.addWidget(self.nav_next_btn)
        self.horizontalLayout.addLayout(self.horizontalLayout_2)
        spacerItem1 = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(NavigationWidget)
        QtCore.QMetaObject.connectSlotsByName(NavigationWidget)

    def retranslateUi(self, NavigationWidget):
        NavigationWidget.setWindowTitle(QtGui.QApplication.translate("NavigationWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
