# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'note_widget.ui'
#
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!
#
# stewartb - 
# no they wont anymore, im working with this by hand now.
# i have removed this class from the auto-generate script.
#
# styling NoteWidget seems to effect all the notes in the scroller.

from tank.platform.qt import QtCore, QtGui

class Ui_NoteWidget(object):
    def setupUi(self, NoteWidget):
        # NoteWidget.setStyleSheet("#content { font-size: 12px; margin-bottom: 6px; }\
        #     #header_left { font-size: 12px;  color: rgb(150,100,100); } \
        #     #date { font-size: 10px; color: rgb(100,100,100);} \
        #     #content { font-size: 12px; } \
        #     #links { font-size: 0px; } \
        #     #design_frame { border-left: 3px solid #444444; } ")
        NoteWidget.setObjectName("NoteWidget")
        NoteWidget.resize(357, 142)

        self.horizontalLayout_2 = QtGui.QHBoxLayout(NoteWidget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, 8, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.user_thumb = UserThumbnail(NoteWidget)
        self.user_thumb.setMinimumSize(QtCore.QSize(40, 40))
        self.user_thumb.setMaximumSize(QtCore.QSize(40, 40))
        self.user_thumb.setText("")
        self.user_thumb.setPixmap(QtGui.QPixmap(":/tk_framework_qtwidgets.activity_stream/default_user.png"))
        self.user_thumb.setScaledContents(True)
        self.user_thumb.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.user_thumb.setObjectName("user_thumb")
        
        self.verticalLayout_2.addWidget(self.user_thumb)
        
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        
        self.verticalLayout_2.addItem(spacerItem)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.frame = QtGui.QFrame(NoteWidget)
        #self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        #self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSpacing(1)
        
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

        
        self.header_left = QtGui.QLabel()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.header_left.sizePolicy().hasHeightForWidth())
        #self.header_left.setSizePolicy(sizePolicy)
        self.header_left.setText("")
        #self.header_left.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        #self.header_left.setWordWrap(True)
        self.header_left.setObjectName("header_left")
        
        self.horizontalLayout.addWidget(self.header_left)
        
        self.date = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date.sizePolicy().hasHeightForWidth())
        # self.date.setSizePolicy(sizePolicy)
        self.date.setText("")
        #self.date.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        #self.date.setWordWrap(True)
        self.date.setObjectName("date")
        self.horizontalLayout.addWidget(self.date)
        self.horizontalLayout.addStretch(1)

        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.links = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.links.sizePolicy().hasHeightForWidth())
        self.links.setSizePolicy(sizePolicy)
        self.links.setText("")
        self.links.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.links.setWordWrap(True)
        self.links.setObjectName("links")
        
        # self.verticalLayout.addWidget(self.links)
        
        self.content = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.content.sizePolicy().hasHeightForWidth())
        self.content.setSizePolicy(sizePolicy)
        self.content.setText("")
        self.content.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.content.setWordWrap(True)
        self.content.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.content.setObjectName("content")
        

        self.design_frame = QtGui.QFrame(NoteWidget)
        self.design_frame.setMinimumSize(QtCore.QSize(16, 15))
        self.design_frame.setObjectName("design_frame")



        self.verticalLayout.addWidget(self.content)


        self.reply_layout = QtGui.QVBoxLayout()
        self.reply_layout.setSpacing(0)
        self.reply_layout.setContentsMargins(0, 0, -1, -1)
        self.reply_layout.setObjectName("reply_layout")

        self.left_bar_layout = QtGui.QHBoxLayout()
        self.left_bar_layout.addWidget(self.design_frame)
        self.left_bar_layout.addLayout(self.reply_layout)

        #self.verticalLayout.addLayout(self.reply_layout)
        self.verticalLayout.addLayout(self.left_bar_layout)

        self.horizontalLayout_2.addWidget(self.frame)

        self.verticalLayout.addWidget(self.links)

        self.retranslateUi(NoteWidget)
        QtCore.QMetaObject.connectSlotsByName(NoteWidget)

    def retranslateUi(self, NoteWidget):
        NoteWidget.setWindowTitle(QtGui.QApplication.translate("NoteWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

from ..label_widgets import UserThumbnail
from . import resources_rc
