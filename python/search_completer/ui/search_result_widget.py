# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_result_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_SearchResultWidget(object):
    def setupUi(self, SearchResultWidget):
        SearchResultWidget.setObjectName("SearchResultWidget")
        SearchResultWidget.resize(260, 44)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(SearchResultWidget)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.box = QtGui.QFrame(SearchResultWidget)
        self.box.setFrameShape(QtGui.QFrame.NoFrame)
        self.box.setObjectName("box")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setContentsMargins(8, 2, 1, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.thumbnail = QtGui.QLabel(self.box)
        self.thumbnail.setMinimumSize(QtCore.QSize(48, 38))
        self.thumbnail.setMaximumSize(QtCore.QSize(48, 38))
        self.thumbnail.setText("")
        self.thumbnail.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.global_search_widget/rect_512x400.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail.setObjectName("thumbnail")
        self.horizontalLayout_2.addWidget(self.thumbnail)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(self.box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addWidget(self.box)

        self.retranslateUi(SearchResultWidget)
        QtCore.QMetaObject.connectSlotsByName(SearchResultWidget)

    def retranslateUi(self, SearchResultWidget):
        SearchResultWidget.setWindowTitle(QtGui.QApplication.translate("SearchResultWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SearchResultWidget", "Body text\n"
"hello", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
