# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_SearchWidget(object):
    def setupUi(self, SearchWidget):
        SearchWidget.setObjectName("SearchWidget")
        SearchWidget.resize(312, 24)
        self.horizontalLayout = QtGui.QHBoxLayout(SearchWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.search_edit = QtGui.QLineEdit(SearchWidget)
        self.search_edit.setMinimumSize(QtCore.QSize(0, 24))
        self.search_edit.setStyleSheet("#search_edit {\n"
"background-image: url(:/tk-framework-qtwidgets/search_widget/search.png);\n"
"background-repeat: no-repeat;\n"
"background-position: center left;\n"
"border-radius: 5px;\n"
"padding-left:20px;\n"
"padding-right:20px;\n"
"}")
        self.search_edit.setObjectName("search_edit")
        self.horizontalLayout.addWidget(self.search_edit)
        self.horizontalLayout.setStretch(0, 1)

        self.retranslateUi(SearchWidget)
        QtCore.QMetaObject.connectSlotsByName(SearchWidget)

    def retranslateUi(self, SearchWidget):
        SearchWidget.setWindowTitle(QtGui.QApplication.translate("SearchWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
