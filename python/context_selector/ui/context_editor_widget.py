# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'context_editor_widget.ui'
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


from ..qtwidgets import GlobalSearchWidget

from  . import resources_rc

class Ui_ContextWidget(object):
    def setupUi(self, ContextWidget):
        if not ContextWidget.objectName():
            ContextWidget.setObjectName(u"ContextWidget")
        ContextWidget.resize(285, 89)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ContextWidget.sizePolicy().hasHeightForWidth())
        ContextWidget.setSizePolicy(sizePolicy)
        ContextWidget.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(ContextWidget)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(ContextWidget)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)

        self.verticalLayout_2.addWidget(self.label)

        self.edit_widget = QWidget(ContextWidget)
        self.edit_widget.setObjectName(u"edit_widget")
        self.verticalLayout = QVBoxLayout(self.edit_widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.task_label = QLabel(self.edit_widget)
        self.task_label.setObjectName(u"task_label")
        self.task_label.setMinimumSize(QSize(0, 0))
        self.task_label.setMaximumSize(QSize(16777215, 32))
        self.task_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.task_label.setOpenExternalLinks(True)
        self.task_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.task_label, 0, 0, 1, 1)

        self.task_widgets_layout = QHBoxLayout()
        self.task_widgets_layout.setSpacing(4)
        self.task_widgets_layout.setObjectName(u"task_widgets_layout")
        self.task_widgets_layout.setContentsMargins(-1, -1, -1, 1)
        self.task_display = QLabel(self.edit_widget)
        self.task_display.setObjectName(u"task_display")
        self.task_display.setMinimumSize(QSize(0, 0))
        self.task_display.setMaximumSize(QSize(16777215, 32))
        self.task_display.setMargin(4)
        self.task_display.setOpenExternalLinks(True)
        self.task_display.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.task_widgets_layout.addWidget(self.task_display)

        self.task_search_layout = QHBoxLayout()
        self.task_search_layout.setSpacing(0)
        self.task_search_layout.setObjectName(u"task_search_layout")
        self.task_search = GlobalSearchWidget(self.edit_widget)
        self.task_search.setObjectName(u"task_search")
        self.task_search.setMinimumSize(QSize(0, 32))
        self.task_search.setMaximumSize(QSize(16777215, 32))

        self.task_search_layout.addWidget(self.task_search)

        self.task_menu_btn = QToolButton(self.edit_widget)
        self.task_menu_btn.setObjectName(u"task_menu_btn")
        self.task_menu_btn.setMinimumSize(QSize(32, 32))
        self.task_menu_btn.setMaximumSize(QSize(32, 32))
        self.task_menu_btn.setFocusPolicy(Qt.NoFocus)
        self.task_menu_btn.setLayoutDirection(Qt.LeftToRight)
        icon = QIcon()
        icon.addFile(u":/tk_framework_qtwidgets.context_selector/down_arrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.task_menu_btn.setIcon(icon)
        self.task_menu_btn.setIconSize(QSize(32, 32))
        self.task_menu_btn.setCheckable(False)
        self.task_menu_btn.setPopupMode(QToolButton.InstantPopup)

        self.task_search_layout.addWidget(self.task_menu_btn)

        self.task_search_layout.setStretch(0, 100)
        self.task_search_layout.setStretch(1, 1)

        self.task_widgets_layout.addLayout(self.task_search_layout)

        self.task_search_btn = QToolButton(self.edit_widget)
        self.task_search_btn.setObjectName(u"task_search_btn")
        self.task_search_btn.setMinimumSize(QSize(32, 32))
        self.task_search_btn.setMaximumSize(QSize(32, 32))
        self.task_search_btn.setFocusPolicy(Qt.NoFocus)
        icon1 = QIcon()
        icon1.addFile(u":/tk_framework_qtwidgets.context_selector/search.png", QSize(), QIcon.Normal, QIcon.Off)
        self.task_search_btn.setIcon(icon1)
        self.task_search_btn.setIconSize(QSize(32, 32))
        self.task_search_btn.setCheckable(True)

        self.task_widgets_layout.addWidget(self.task_search_btn)

        self.task_widgets_layout.setStretch(0, 1)
        self.task_widgets_layout.setStretch(1, 100)
        self.task_widgets_layout.setStretch(2, 1)

        self.gridLayout.addLayout(self.task_widgets_layout, 0, 1, 1, 1)

        self.link_label = QLabel(self.edit_widget)
        self.link_label.setObjectName(u"link_label")
        self.link_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.link_label.setOpenExternalLinks(True)
        self.link_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.link_label, 1, 0, 1, 1)

        self.link_widgets_layout = QHBoxLayout()
        self.link_widgets_layout.setSpacing(4)
        self.link_widgets_layout.setObjectName(u"link_widgets_layout")
        self.link_widgets_layout.setContentsMargins(-1, 1, -1, -1)
        self.link_display = QLabel(self.edit_widget)
        self.link_display.setObjectName(u"link_display")
        self.link_display.setMinimumSize(QSize(0, 0))
        self.link_display.setMaximumSize(QSize(16777215, 32))
        self.link_display.setMargin(4)
        self.link_display.setOpenExternalLinks(True)
        self.link_display.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.link_widgets_layout.addWidget(self.link_display)

        self.link_search = GlobalSearchWidget(self.edit_widget)
        self.link_search.setObjectName(u"link_search")
        self.link_search.setMinimumSize(QSize(0, 32))
        self.link_search.setMaximumSize(QSize(16777215, 32))

        self.link_widgets_layout.addWidget(self.link_search)

        self.link_search_btn = QToolButton(self.edit_widget)
        self.link_search_btn.setObjectName(u"link_search_btn")
        self.link_search_btn.setMinimumSize(QSize(32, 32))
        self.link_search_btn.setMaximumSize(QSize(32, 32))
        self.link_search_btn.setFocusPolicy(Qt.NoFocus)
        self.link_search_btn.setIcon(icon1)
        self.link_search_btn.setIconSize(QSize(32, 32))
        self.link_search_btn.setCheckable(True)

        self.link_widgets_layout.addWidget(self.link_search_btn)

        self.link_widgets_layout.setStretch(0, 1)
        self.link_widgets_layout.setStretch(1, 100)
        self.link_widgets_layout.setStretch(2, 1)

        self.gridLayout.addLayout(self.link_widgets_layout, 1, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 100)

        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalLayout_2.addWidget(self.edit_widget)

        self.retranslateUi(ContextWidget)

        QMetaObject.connectSlotsByName(ContextWidget)
    # setupUi

    def retranslateUi(self, ContextWidget):
        ContextWidget.setWindowTitle(QCoreApplication.translate("ContextWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("ContextWidget", u"Task and Entity Link to apply to the selected item:", None))
#if QT_CONFIG(tooltip)
        self.task_label.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.task_label.setText(QCoreApplication.translate("ContextWidget", u"Task: ", None))
        self.task_display.setText(QCoreApplication.translate("ContextWidget", u"Loading...", None))
        self.task_menu_btn.setText("")
#if QT_CONFIG(tooltip)
        self.task_search_btn.setToolTip(QCoreApplication.translate("ContextWidget", u"<html><head/><body><p>Toggle this button to allow searching for a Task to associate with the selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.task_search_btn.setText(QCoreApplication.translate("ContextWidget", u"...", None))
        self.link_label.setText(QCoreApplication.translate("ContextWidget", u"Link: ", None))
        self.link_display.setText(QCoreApplication.translate("ContextWidget", u"Loading...", None))
#if QT_CONFIG(tooltip)
        self.link_search_btn.setToolTip(QCoreApplication.translate("ContextWidget", u"<html><head/><body><p>Toggle this button to allow searching for an entity to link to the selected item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.link_search_btn.setText(QCoreApplication.translate("ContextWidget", u"...", None))
    # retranslateUi
