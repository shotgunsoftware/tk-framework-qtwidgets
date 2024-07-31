# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'navigation_widget.ui'
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

class Ui_NavigationWidget(object):
    def setupUi(self, NavigationWidget):
        if not NavigationWidget.objectName():
            NavigationWidget.setObjectName(u"NavigationWidget")
        NavigationWidget.resize(119, 38)
        self.horizontalLayout = QHBoxLayout(NavigationWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.nav_home_btn = QToolButton(NavigationWidget)
        self.nav_home_btn.setObjectName(u"nav_home_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nav_home_btn.sizePolicy().hasHeightForWidth())
        self.nav_home_btn.setSizePolicy(sizePolicy)
        self.nav_home_btn.setMinimumSize(QSize(39, 36))
        self.nav_home_btn.setMaximumSize(QSize(39, 36))
        self.nav_home_btn.setBaseSize(QSize(0, 0))
        self.nav_home_btn.setStyleSheet(u"#nav_home_btn{\n"
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

        self.horizontalLayout_2.addWidget(self.nav_home_btn)

        self.nav_prev_btn = QToolButton(NavigationWidget)
        self.nav_prev_btn.setObjectName(u"nav_prev_btn")
        sizePolicy.setHeightForWidth(self.nav_prev_btn.sizePolicy().hasHeightForWidth())
        self.nav_prev_btn.setSizePolicy(sizePolicy)
        self.nav_prev_btn.setMinimumSize(QSize(34, 36))
        self.nav_prev_btn.setMaximumSize(QSize(34, 36))
        self.nav_prev_btn.setBaseSize(QSize(0, 0))
        self.nav_prev_btn.setStyleSheet(u"#nav_prev_btn{\n"
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

        self.horizontalLayout_2.addWidget(self.nav_prev_btn)

        self.nav_next_btn = QToolButton(NavigationWidget)
        self.nav_next_btn.setObjectName(u"nav_next_btn")
        sizePolicy.setHeightForWidth(self.nav_next_btn.sizePolicy().hasHeightForWidth())
        self.nav_next_btn.setSizePolicy(sizePolicy)
        self.nav_next_btn.setMinimumSize(QSize(34, 36))
        self.nav_next_btn.setMaximumSize(QSize(34, 36))
        self.nav_next_btn.setBaseSize(QSize(0, 0))
        self.nav_next_btn.setStyleSheet(u"#nav_next_btn{\n"
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

        self.horizontalLayout_2.addWidget(self.nav_next_btn)

        self.horizontalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(NavigationWidget)

        QMetaObject.connectSlotsByName(NavigationWidget)
    # setupUi

    def retranslateUi(self, NavigationWidget):
        NavigationWidget.setWindowTitle(QCoreApplication.translate("NavigationWidget", u"Form", None))
#if QT_CONFIG(accessibility)
        self.nav_home_btn.setAccessibleName(QCoreApplication.translate("NavigationWidget", u"nav_home_btn", None))
#endif // QT_CONFIG(accessibility)
        self.nav_home_btn.setText("")
#if QT_CONFIG(accessibility)
        self.nav_prev_btn.setAccessibleName(QCoreApplication.translate("NavigationWidget", u"nav_prev_btn", None))
#endif // QT_CONFIG(accessibility)
        self.nav_prev_btn.setText("")
#if QT_CONFIG(accessibility)
        self.nav_next_btn.setAccessibleName(QCoreApplication.translate("NavigationWidget", u"nav_next_btn", None))
#endif // QT_CONFIG(accessibility)
        self.nav_next_btn.setText("")
    # retranslateUi
