# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'note_input_widget.ui'
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


from ..note_editor import NoteEditor
from ..sg_qwidgets import SGSubmitPushButton
from ..sg_qwidgets import SGCancelPushButton

from  . import resources_rc

class Ui_NoteInputWidget(object):
    def setupUi(self, NoteInputWidget):
        if not NoteInputWidget.objectName():
            NoteInputWidget.setObjectName(u"NoteInputWidget")
        NoteInputWidget.resize(848, 502)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NoteInputWidget.sizePolicy().hasHeightForWidth())
        NoteInputWidget.setSizePolicy(sizePolicy)
        self.verticalLayout_5 = QVBoxLayout(NoteInputWidget)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.stacked_widget = QStackedWidget(NoteInputWidget)
        self.stacked_widget.setObjectName(u"stacked_widget")
        self.note_editor_page = QWidget()
        self.note_editor_page.setObjectName(u"note_editor_page")
        self.verticalLayout_2 = QVBoxLayout(self.note_editor_page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(7)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.text_entry = NoteEditor(self.note_editor_page)
        self.text_entry.setObjectName(u"text_entry")
        self.text_entry.setFocusPolicy(Qt.ClickFocus)

        self.verticalLayout.addWidget(self.text_entry)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(7)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, 3, -1, 3)
        self.screenshot = QToolButton(self.note_editor_page)
        self.screenshot.setObjectName(u"screenshot")
        icon = QIcon()
        icon.addFile(u":/tk_framework_qtwidgets.note_input_widget/camera_hl.png", QSize(), QIcon.Normal, QIcon.Off)
        self.screenshot.setIcon(icon)
        self.screenshot.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.screenshot.setAutoRaise(True)

        self.horizontalLayout_5.addWidget(self.screenshot)

        self.attach = QToolButton(self.note_editor_page)
        self.attach.setObjectName(u"attach")
        icon1 = QIcon()
        icon1.addFile(u":/tk_framework_qtwidgets.note_input_widget/paper_clip.png", QSize(), QIcon.Normal, QIcon.Off)
        self.attach.setIcon(icon1)
        self.attach.setAutoRaise(True)

        self.horizontalLayout_5.addWidget(self.attach)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.close = SGCancelPushButton(self.note_editor_page)
        self.close.setObjectName(u"close")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.close.sizePolicy().hasHeightForWidth())
        self.close.setSizePolicy(sizePolicy1)

        self.horizontalLayout_5.addWidget(self.close)

        self.submit = SGSubmitPushButton(self.note_editor_page)
        self.submit.setObjectName(u"submit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.submit.sizePolicy().hasHeightForWidth())
        self.submit.setSizePolicy(sizePolicy2)
        self.submit.setIconSize(QSize(20, 20))
        self.submit.setFlat(False)

        self.horizontalLayout_5.addWidget(self.submit)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.thumbnail = QLabel(self.note_editor_page)
        self.thumbnail.setObjectName(u"thumbnail")
        self.thumbnail.setEnabled(True)
        self.thumbnail.setMinimumSize(QSize(96, 75))
        self.thumbnail.setMaximumSize(QSize(96, 75))
        self.thumbnail.setPixmap(QPixmap(u":/tk_framework_qtwidgets/rect_512x400.png"))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)
        self.thumbnail.setMargin(0)

        self.horizontalLayout.addWidget(self.thumbnail)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.stacked_widget.addWidget(self.note_editor_page)
        self.preview_page = QWidget()
        self.preview_page.setObjectName(u"preview_page")
        self.verticalLayout_3 = QVBoxLayout(self.preview_page)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.new_note_frame = QFrame(self.preview_page)
        self.new_note_frame.setObjectName(u"new_note_frame")
        self.new_note_frame.setStyleSheet(u"")
        self.new_note_frame.setFrameShape(QFrame.StyledPanel)
        self.new_note_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.new_note_frame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.new_note_placeholder = QLabel(self.new_note_frame)
        self.new_note_placeholder.setObjectName(u"new_note_placeholder")
        self.new_note_placeholder.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.verticalLayout_4.addWidget(self.new_note_placeholder)

        self.verticalLayout_3.addWidget(self.new_note_frame)

        self.stacked_widget.addWidget(self.preview_page)
        self.attachments_page = QWidget()
        self.attachments_page.setObjectName(u"attachments_page")
        self.horizontalLayout_2 = QHBoxLayout(self.attachments_page)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, -1, 0)
        self.attachment_list = QWidget(self.attachments_page)
        self.attachment_list.setObjectName(u"attachment_list")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.attachment_list.sizePolicy().hasHeightForWidth())
        self.attachment_list.setSizePolicy(sizePolicy3)
        self.attachments_list_layout = QVBoxLayout(self.attachment_list)
        self.attachments_list_layout.setSpacing(7)
        self.attachments_list_layout.setObjectName(u"attachments_list_layout")
        self.attachments_list_layout.setContentsMargins(0, 0, 0, 0)
        self.attachment_list_tree = QTreeWidget(self.attachment_list)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.attachment_list_tree.setHeaderItem(__qtreewidgetitem)
        self.attachment_list_tree.setObjectName(u"attachment_list_tree")
        self.attachment_list_tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.attachment_list_tree.setRootIsDecorated(False)
        self.attachment_list_tree.setItemsExpandable(False)
        self.attachment_list_tree.setHeaderHidden(True)
        self.attachment_list_tree.setExpandsOnDoubleClick(False)

        self.attachments_list_layout.addWidget(self.attachment_list_tree)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(7)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 3, -1, 3)
        self.add_button = QToolButton(self.attachment_list)
        self.add_button.setObjectName(u"add_button")
        icon2 = QIcon()
        icon2.addFile(u":/tk_framework_qtwidgets.note_input_widget/plus.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_button.setIcon(icon2)
        self.add_button.setAutoRaise(True)

        self.horizontalLayout_4.addWidget(self.add_button)

        self.remove_button = QToolButton(self.attachment_list)
        self.remove_button.setObjectName(u"remove_button")
        icon3 = QIcon()
        icon3.addFile(u":/tk_framework_qtwidgets.note_input_widget/minus.png", QSize(), QIcon.Normal, QIcon.Off)
        self.remove_button.setIcon(icon3)
        self.remove_button.setAutoRaise(True)

        self.horizontalLayout_4.addWidget(self.remove_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.close_attachments = SGCancelPushButton(self.attachment_list)
        self.close_attachments.setObjectName(u"close_attachments")

        self.horizontalLayout_4.addWidget(self.close_attachments)

        self.add_attachments = SGSubmitPushButton(self.attachment_list)
        self.add_attachments.setObjectName(u"add_attachments")

        self.horizontalLayout_4.addWidget(self.add_attachments)

        self.attachments_list_layout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3.addWidget(self.attachment_list)

        self.horizontalLayout_2.addLayout(self.horizontalLayout_3)

        self.stacked_widget.addWidget(self.attachments_page)

        self.verticalLayout_5.addWidget(self.stacked_widget)

        self.retranslateUi(NoteInputWidget)

        self.stacked_widget.setCurrentIndex(2)

        QMetaObject.connectSlotsByName(NoteInputWidget)
    # setupUi

    def retranslateUi(self, NoteInputWidget):
        NoteInputWidget.setWindowTitle(QCoreApplication.translate("NoteInputWidget", u"Form", None))
        self.text_entry.setPlaceholderText(QCoreApplication.translate("NoteInputWidget", u"You can add people by referring to them by @name", None))
#if QT_CONFIG(tooltip)
        self.screenshot.setToolTip(QCoreApplication.translate("NoteInputWidget", u"Take a screenshot", None))
#endif // QT_CONFIG(tooltip)
        self.screenshot.setText(QCoreApplication.translate("NoteInputWidget", u"Attach Screenshot", None))
#if QT_CONFIG(tooltip)
        self.attach.setToolTip(QCoreApplication.translate("NoteInputWidget", u"Attach Files", None))
#endif // QT_CONFIG(tooltip)
        self.attach.setText(QCoreApplication.translate("NoteInputWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.close.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.close.setText("")
#if QT_CONFIG(tooltip)
        self.submit.setToolTip(QCoreApplication.translate("NoteInputWidget", u"Create a new note", None))
#endif // QT_CONFIG(tooltip)
        self.submit.setText("")
        self.thumbnail.setText("")
        self.new_note_placeholder.setText(QCoreApplication.translate("NoteInputWidget", u"Click to create a new note...", None))
#if QT_CONFIG(tooltip)
        self.add_button.setToolTip(QCoreApplication.translate("NoteInputWidget", u"Add attachment to the list. Click \"Attach All\" to add all attachments to the note.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.add_button.setAccessibleName(QCoreApplication.translate("NoteInputWidget", u"add_button", None))
#endif // QT_CONFIG(accessibility)
        self.add_button.setText(QCoreApplication.translate("NoteInputWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.remove_button.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.remove_button.setAccessibleName(QCoreApplication.translate("NoteInputWidget", u"remove_button", None))
#endif // QT_CONFIG(accessibility)
        self.remove_button.setText(QCoreApplication.translate("NoteInputWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.close_attachments.setToolTip(QCoreApplication.translate("NoteInputWidget", u"Cancel adding the attachments to the note", None))
#endif // QT_CONFIG(tooltip)
        self.close_attachments.setText("")
#if QT_CONFIG(tooltip)
        self.add_attachments.setToolTip(QCoreApplication.translate("NoteInputWidget", u"Attach files to the note. Attachments will be created when the note is submitted.", None))
#endif // QT_CONFIG(tooltip)
        self.add_attachments.setText(QCoreApplication.translate("NoteInputWidget", u"Attach All", None))
    # retranslateUi
