# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'browser.ui'
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
from  . import resources_rc

class Ui_Browser(object):
    def setupUi(self, Browser):
        if not Browser.objectName():
            Browser.setObjectName(u"Browser")
        Browser.resize(591, 565)
        self.verticalLayout = QVBoxLayout(Browser)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.browser_header = QFrame(Browser)
        self.browser_header.setObjectName(u"browser_header")
        self.browser_header.setMinimumSize(QSize(0, 44))
        self.browser_header.setMaximumSize(QSize(16777215, 44))
        self.browser_header.setStyleSheet(u"")
        self.browser_header.setFrameShape(QFrame.StyledPanel)
        self.browser_header.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.browser_header)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(12, 3, 12, 3)
        self.label = QLabel(self.browser_header)
        self.label.setObjectName(u"label")

        self.horizontalLayout_4.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.search = QLineEdit(self.browser_header)
        self.search.setObjectName(u"search")
        self.search.setMinimumSize(QSize(150, 0))
        self.search.setMaximumSize(QSize(150, 16777215))
        self.search.setStyleSheet(u"border-width: 1px;\n"
"background-image: url(:/tk_framework_qtwidgets.browser_widget/search.png);\n"
"background-repeat: no-repeat;\n"
"background-position: center left;\n"
"border-style: inset;\n"
"border-color: #535353;\n"
"border-radius: 9px;\n"
"padding-left: 15px")

        self.horizontalLayout_4.addWidget(self.search)

        self.verticalLayout.addWidget(self.browser_header)

        self.main_pages = QStackedWidget(Browser)
        self.main_pages.setObjectName(u"main_pages")
        self.items_page = QWidget()
        self.items_page.setObjectName(u"items_page")
        self.horizontalLayout_3 = QHBoxLayout(self.items_page)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.scroll_area = QScrollArea(self.items_page)
        self.scroll_area.setObjectName(u"scroll_area")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 589, 519))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.load_all_top = QToolButton(self.scrollAreaWidgetContents)
        self.load_all_top.setObjectName(u"load_all_top")

        self.horizontalLayout_7.addWidget(self.load_all_top)

        self.verticalLayout_4.addLayout(self.horizontalLayout_7)

        self.scroll_area_layout = QVBoxLayout()
        self.scroll_area_layout.setSpacing(0)
        self.scroll_area_layout.setObjectName(u"scroll_area_layout")

        self.verticalLayout_4.addLayout(self.scroll_area_layout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.load_all_bottom = QToolButton(self.scrollAreaWidgetContents)
        self.load_all_bottom.setObjectName(u"load_all_bottom")

        self.horizontalLayout_8.addWidget(self.load_all_bottom)

        self.verticalLayout_4.addLayout(self.horizontalLayout_8)

        self.scroll_area.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_3.addWidget(self.scroll_area)

        self.main_pages.addWidget(self.items_page)
        self.loading_page = QWidget()
        self.loading_page.setObjectName(u"loading_page")
        self.loading_page.setStyleSheet(u"")
        self.horizontalLayout = QHBoxLayout(self.loading_page)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.progress_bar = QLabel(self.loading_page)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setLayoutDirection(Qt.LeftToRight)
        self.progress_bar.setStyleSheet(u"#progress_bar {\n"
"border-style: solid;\n"
"border-width: 1px;\n"
"border-radius: 2px;\n"
"border-color: rgb(32,32,32);\n"
"}")
        self.progress_bar.setPixmap(QPixmap(u":/tk_framework_qtwidgets.browser_widget/progress_bar_1.png"))
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.progress_bar)

        self.main_pages.addWidget(self.loading_page)
        self.status_page = QWidget()
        self.status_page.setObjectName(u"status_page")
        self.horizontalLayout_2 = QHBoxLayout(self.status_page)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.status_message = QLabel(self.status_page)
        self.status_message.setObjectName(u"status_message")
        self.status_message.setLayoutDirection(Qt.LeftToRight)
        self.status_message.setStyleSheet(u"#status_message {\n"
"border-style: solid;\n"
"border-width: 1px;\n"
"border-radius: 2px;\n"
"border-color: rgb(32,32,32);\n"
"}")
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setWordWrap(True)

        self.horizontalLayout_2.addWidget(self.status_message)

        self.main_pages.addWidget(self.status_page)

        self.verticalLayout.addWidget(self.main_pages)

        self.retranslateUi(Browser)

        self.main_pages.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Browser)
    # setupUi

    def retranslateUi(self, Browser):
        Browser.setWindowTitle(QCoreApplication.translate("Browser", u"Form", None))
        self.label.setText(QCoreApplication.translate("Browser", u"<big>Browser Title</big>", None))
        self.load_all_top.setText(QCoreApplication.translate("Browser", u"Showing 50 out of 250 matches. Click to load all...", None))
        self.load_all_bottom.setText(QCoreApplication.translate("Browser", u"Showing 50 out of 250 matches. Click to load all...", None))
        self.progress_bar.setText("")
        self.status_message.setText(QCoreApplication.translate("Browser", u"Sorry, no items found!", None))
    # retranslateUi
