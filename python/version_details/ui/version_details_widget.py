# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'version_details_widget.ui'
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


from ..qtwidgets import ShotgunEntityCardWidget
from ..qtwidgets import ActivityStreamWidget
from ..qtwidgets import SearchWidget

from  . import resources_rc

class Ui_VersionDetailsWidget(object):
    def setupUi(self, VersionDetailsWidget):
        if not VersionDetailsWidget.objectName():
            VersionDetailsWidget.setObjectName(u"VersionDetailsWidget")
        VersionDetailsWidget.resize(390, 737)
        self.verticalLayout_17 = QVBoxLayout(VersionDetailsWidget)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.details_title_bar = QFrame(VersionDetailsWidget)
        self.details_title_bar.setObjectName(u"details_title_bar")
        self.details_title_bar.setMinimumSize(QSize(0, 13))
        self.details_title_bar.setMaximumSize(QSize(16777215, 16777215))
        self.details_title_bar.setFrameShape(QFrame.NoFrame)
        self.details_title_bar.setFrameShadow(QFrame.Plain)
        self.details_title_bar.setLineWidth(0)
        self.horizontalLayout_9 = QHBoxLayout(self.details_title_bar)
        self.horizontalLayout_9.setSpacing(3)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 5, 5, 0)
        self.horizontalSpacer_2 = QSpacerItem(350, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_2)

        self.float_button = QToolButton(self.details_title_bar)
        self.float_button.setObjectName(u"float_button")
        self.float_button.setMaximumSize(QSize(8, 8))
        icon = QIcon()
        icon.addFile(u":/version_details/undock.png", QSize(), QIcon.Normal, QIcon.Off)
        icon.addFile(u":/version_details/dock.png", QSize(), QIcon.Normal, QIcon.On)
        icon.addFile(u":/version_details/undock_hover.png", QSize(), QIcon.Active, QIcon.Off)
        icon.addFile(u":/version_details/dock_hover.png", QSize(), QIcon.Active, QIcon.On)
        icon.addFile(u":/version_details/undock_hover.png", QSize(), QIcon.Selected, QIcon.Off)
        icon.addFile(u":/version_details/undock_hover.png", QSize(), QIcon.Selected, QIcon.On)
        self.float_button.setIcon(icon)
        self.float_button.setCheckable(True)
        self.float_button.setAutoRaise(True)

        self.horizontalLayout_9.addWidget(self.float_button)

        self.close_button = QToolButton(self.details_title_bar)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setMaximumSize(QSize(8, 8))
        icon1 = QIcon()
        icon1.addFile(u":/version_details/close.png", QSize(), QIcon.Normal, QIcon.Off)
        icon1.addFile(u":/version_details/close.png", QSize(), QIcon.Normal, QIcon.On)
        icon1.addFile(u":/version_details/close_hover.png", QSize(), QIcon.Active, QIcon.Off)
        icon1.addFile(u":/version_details/close_hover.png", QSize(), QIcon.Active, QIcon.On)
        icon1.addFile(u":/version_details/close_hover.png", QSize(), QIcon.Selected, QIcon.Off)
        icon1.addFile(u":/version_details/close_hover.png", QSize(), QIcon.Selected, QIcon.On)
        self.close_button.setIcon(icon1)
        self.close_button.setAutoRaise(True)

        self.horizontalLayout_9.addWidget(self.close_button)

        self.verticalLayout_17.addWidget(self.details_title_bar)

        self.pages = QStackedWidget(VersionDetailsWidget)
        self.pages.setObjectName(u"pages")
        self.main_page = QWidget()
        self.main_page.setObjectName(u"main_page")
        self.verticalLayout = QVBoxLayout(self.main_page)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.entity_tab_widget = QTabWidget(self.main_page)
        self.entity_tab_widget.setObjectName(u"entity_tab_widget")
        self.entity_tab_widget.setFocusPolicy(Qt.NoFocus)
        self.entity_tab_widget.setStyleSheet(u"QTabWidget::tab-bar { alignment: center; border: none }")
        self.entity_note_tab = QWidget()
        self.entity_note_tab.setObjectName(u"entity_note_tab")
        self.verticalLayout_3 = QVBoxLayout(self.entity_note_tab)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(8, 5, 8, 5)
        self.info_layout = QHBoxLayout()
        self.info_layout.setSpacing(0)
        self.info_layout.setObjectName(u"info_layout")
        self.info_layout.setContentsMargins(0, 0, -1, 0)
        self.widget = QWidget(self.entity_note_tab)
        self.widget.setObjectName(u"widget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(10, 0, 0, 0)
        self.current_version_card = ShotgunEntityCardWidget(self.widget)
        self.current_version_card.setObjectName(u"current_version_card")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.current_version_card.sizePolicy().hasHeightForWidth())
        self.current_version_card.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.current_version_card)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, -1, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, 2, -1)
        self.shotgun_nav_button = QToolButton(self.widget)
        self.shotgun_nav_button.setObjectName(u"shotgun_nav_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.shotgun_nav_button.sizePolicy().hasHeightForWidth())
        self.shotgun_nav_button.setSizePolicy(sizePolicy2)
        self.shotgun_nav_button.setMaximumSize(QSize(15, 15))
        icon2 = QIcon()
        icon2.addFile(u":/version_details/navigate_out.png", QSize(), QIcon.Normal, QIcon.On)
        icon2.addFile(u":/version_details/navigate_out_hover.png", QSize(), QIcon.Active, QIcon.On)
        icon2.addFile(u":/version_details/navigate_out_hover.png", QSize(), QIcon.Selected, QIcon.On)
        self.shotgun_nav_button.setIcon(icon2)
        self.shotgun_nav_button.setAutoRaise(True)

        self.horizontalLayout.addWidget(self.shotgun_nav_button)

        self.pin_button = QToolButton(self.widget)
        self.pin_button.setObjectName(u"pin_button")
        sizePolicy2.setHeightForWidth(self.pin_button.sizePolicy().hasHeightForWidth())
        self.pin_button.setSizePolicy(sizePolicy2)
        self.pin_button.setMaximumSize(QSize(15, 15))
        icon3 = QIcon()
        icon3.addFile(u":/version_details/tack_up.png", QSize(), QIcon.Normal, QIcon.On)
        icon3.addFile(u":/version_details/tack_hover.png", QSize(), QIcon.Active, QIcon.On)
        icon3.addFile(u":/version_details/tack_hover.png", QSize(), QIcon.Selected, QIcon.On)
        self.pin_button.setIcon(icon3)
        self.pin_button.setCheckable(True)
        self.pin_button.setAutoRaise(True)

        self.horizontalLayout.addWidget(self.pin_button)

        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.info_layout.addWidget(self.widget)

        self.verticalLayout_3.addLayout(self.info_layout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_3 = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.more_info_button = QToolButton(self.entity_note_tab)
        self.more_info_button.setObjectName(u"more_info_button")
        self.more_info_button.setStyleSheet(u"QToolButton { border: none; background: transparent; }")
        self.more_info_button.setCheckable(True)
        self.more_info_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.more_info_button.setArrowType(Qt.NoArrow)

        self.horizontalLayout_4.addWidget(self.more_info_button)

        self.more_fields_button = QToolButton(self.entity_note_tab)
        self.more_fields_button.setObjectName(u"more_fields_button")
        self.more_fields_button.setStyleSheet(u"QToolButton { border: none; background: transparent; }")
        self.more_fields_button.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout_4.addWidget(self.more_fields_button)

        self.horizontalSpacer_4 = QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.notes_tab_line = QFrame(self.entity_note_tab)
        self.notes_tab_line.setObjectName(u"notes_tab_line")
        self.notes_tab_line.setFrameShadow(QFrame.Sunken)
        self.notes_tab_line.setFrameShape(QFrame.HLine)

        self.verticalLayout_3.addWidget(self.notes_tab_line)

        self.note_stream_widget = ActivityStreamWidget(self.entity_note_tab)
        self.note_stream_widget.setObjectName(u"note_stream_widget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.note_stream_widget.sizePolicy().hasHeightForWidth())
        self.note_stream_widget.setSizePolicy(sizePolicy3)
        self.note_stream_widget.setStyleSheet(u"border: none")

        self.verticalLayout_3.addWidget(self.note_stream_widget)

        self.entity_tab_widget.addTab(self.entity_note_tab, "")
        self.entity_version_tab = QWidget()
        self.entity_version_tab.setObjectName(u"entity_version_tab")
        self.verticalLayout_2 = QVBoxLayout(self.entity_version_tab)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 0, 5, 5)
        self.version_top_layout = QWidget(self.entity_version_tab)
        self.version_top_layout.setObjectName(u"version_top_layout")
        self.horizontalLayout_5 = QHBoxLayout(self.version_top_layout)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 2, 0, 2)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, -1, -1, -1)
        self.version_fields_button = QToolButton(self.version_top_layout)
        self.version_fields_button.setObjectName(u"version_fields_button")
        self.version_fields_button.setStyleSheet(u"QToolButton { border: none; background: transparent; }")
        self.version_fields_button.setPopupMode(QToolButton.InstantPopup)
        self.version_fields_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout_6.addWidget(self.version_fields_button)

        self.label = QLabel(self.version_top_layout)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(8, 8))
        self.label.setPixmap(QPixmap(u":/version_details/arrow.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_6.addWidget(self.label)

        self.horizontalLayout_3.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, -1, 0, -1)
        self.version_sort_button = QToolButton(self.version_top_layout)
        self.version_sort_button.setObjectName(u"version_sort_button")
        self.version_sort_button.setStyleSheet(u"QToolButton { border: none; background: transparent; }")
        self.version_sort_button.setPopupMode(QToolButton.InstantPopup)

        self.horizontalLayout_7.addWidget(self.version_sort_button)

        self.label_2 = QLabel(self.version_top_layout)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(8, 8))
        self.label_2.setPixmap(QPixmap(u":/version_details/arrow.png"))
        self.label_2.setScaledContents(True)

        self.horizontalLayout_7.addWidget(self.label_2)

        self.horizontalLayout_3.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.version_search = SearchWidget(self.version_top_layout)
        self.version_search.setObjectName(u"version_search")
        self.version_search.setStyleSheet(u"background-color: rgb(50,50,50);")

        self.horizontalLayout_5.addWidget(self.version_search)

        self.verticalLayout_2.addWidget(self.version_top_layout)

        self.line = QFrame(self.entity_version_tab)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setFrameShape(QFrame.HLine)

        self.verticalLayout_2.addWidget(self.line)

        self.entity_version_view = QListView(self.entity_version_tab)
        self.entity_version_view.setObjectName(u"entity_version_view")
        self.entity_version_view.setFocusPolicy(Qt.NoFocus)
        self.entity_version_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entity_version_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.entity_version_view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entity_version_view.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.verticalLayout_2.addWidget(self.entity_version_view)

        self.entity_tab_widget.addTab(self.entity_version_tab, "")

        self.verticalLayout.addWidget(self.entity_tab_widget)

        self.pages.addWidget(self.main_page)
        self.empty_page = QWidget()
        self.empty_page.setObjectName(u"empty_page")
        self.verticalLayout_5 = QVBoxLayout(self.empty_page)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.empty_label = QLabel(self.empty_page)
        self.empty_label.setObjectName(u"empty_label")
        self.empty_label.setPixmap(QPixmap(u":/version_details/panel_empty_background.png"))
        self.empty_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.empty_label)

        self.pages.addWidget(self.empty_page)

        self.verticalLayout_17.addWidget(self.pages)

        self.retranslateUi(VersionDetailsWidget)

        self.pages.setCurrentIndex(0)
        self.entity_tab_widget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(VersionDetailsWidget)
    # setupUi

    def retranslateUi(self, VersionDetailsWidget):
        VersionDetailsWidget.setWindowTitle(QCoreApplication.translate("VersionDetailsWidget", u"Form", None))
        self.float_button.setText(QCoreApplication.translate("VersionDetailsWidget", u"...", None))
        self.close_button.setText(QCoreApplication.translate("VersionDetailsWidget", u"...", None))
        self.shotgun_nav_button.setText(QCoreApplication.translate("VersionDetailsWidget", u"...", None))
        self.pin_button.setText("")
        self.more_info_button.setText(QCoreApplication.translate("VersionDetailsWidget", u"More info", None))
        self.more_fields_button.setText(QCoreApplication.translate("VersionDetailsWidget", u"Fields...", None))
        self.entity_tab_widget.setTabText(self.entity_tab_widget.indexOf(self.entity_note_tab), QCoreApplication.translate("VersionDetailsWidget", u"NOTES", None))
        self.version_fields_button.setText(QCoreApplication.translate("VersionDetailsWidget", u"Fields", None))
        self.label.setText("")
        self.version_sort_button.setText(QCoreApplication.translate("VersionDetailsWidget", u"Sort", None))
        self.label_2.setText("")
        self.entity_tab_widget.setTabText(self.entity_tab_widget.indexOf(self.entity_version_tab), QCoreApplication.translate("VersionDetailsWidget", u"VERSIONS", None))
        self.empty_label.setText("")
    # retranslateUi
