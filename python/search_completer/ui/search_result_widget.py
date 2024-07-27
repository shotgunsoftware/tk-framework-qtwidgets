# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search_result_widget.ui'
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

class Ui_SearchResultWidget(object):
    def setupUi(self, SearchResultWidget):
        if not SearchResultWidget.objectName():
            SearchResultWidget.setObjectName(u"SearchResultWidget")
        SearchResultWidget.resize(260, 44)
        self.horizontalLayout_3 = QHBoxLayout(SearchResultWidget)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.box = QFrame(SearchResultWidget)
        self.box.setObjectName(u"box")
        self.box.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_2 = QHBoxLayout(self.box)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, 2, 1, 2)
        self.thumbnail = QLabel(self.box)
        self.thumbnail.setObjectName(u"thumbnail")
        self.thumbnail.setMinimumSize(QSize(48, 38))
        self.thumbnail.setMaximumSize(QSize(48, 38))
        self.thumbnail.setPixmap(QPixmap(u":/tk_framework_qtwidgets.global_search_widget/rect_512x400.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.thumbnail)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.box)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_3.addWidget(self.box)

        self.retranslateUi(SearchResultWidget)

        QMetaObject.connectSlotsByName(SearchResultWidget)
    # setupUi

    def retranslateUi(self, SearchResultWidget):
        SearchResultWidget.setWindowTitle(QCoreApplication.translate("SearchResultWidget", u"Form", None))
        self.thumbnail.setText("")
        self.label.setText(QCoreApplication.translate("SearchResultWidget", u"Body text\n"
"hello", None))
    # retranslateUi
