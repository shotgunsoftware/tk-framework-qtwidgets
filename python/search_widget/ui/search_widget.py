# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'search_widget.ui'
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
class Ui_SearchWidget(object):
    def setupUi(self, SearchWidget):
        if not SearchWidget.objectName():
            SearchWidget.setObjectName(u"SearchWidget")
        SearchWidget.resize(312, 24)
        self.horizontalLayout = QHBoxLayout(SearchWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.search_edit = QLineEdit(SearchWidget)
        self.search_edit.setObjectName(u"search_edit")
        self.search_edit.setMinimumSize(QSize(0, 24))
        self.search_edit.setStyleSheet(u"#search_edit {\n"
"background-image: url(:/tk-framework-qtwidgets/search_widget/search.png);\n"
"background-repeat: no-repeat;\n"
"background-position: center left;\n"
"border-radius: 5px;\n"
"padding-left:20px;\n"
"padding-right:20px;\n"
"}")
        self.horizontalLayout.addWidget(self.search_edit)
        self.horizontalLayout.setStretch(0, 1)
        self.retranslateUi(SearchWidget)
        QMetaObject.connectSlotsByName(SearchWidget)
    # setupUi
    def retranslateUi(self, SearchWidget):
        SearchWidget.setWindowTitle(QCoreApplication.translate("SearchWidget", u"Form", None))
    # retranslateUi
