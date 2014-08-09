# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/file_browser.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_FileBrowserDialog(object):
    def setupUi(self, FileBrowserDialog):
        FileBrowserDialog.setObjectName("FileBrowserDialog")
        FileBrowserDialog.resize(600, 400)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FileBrowserDialog.sizePolicy().hasHeightForWidth())
        FileBrowserDialog.setSizePolicy(sizePolicy)
        self.fileGroup = QtGui.QGroupBox(FileBrowserDialog)
        self.fileGroup.setGeometry(QtCore.QRect(-1, -1, 605, 405))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileGroup.sizePolicy().hasHeightForWidth())
        self.fileGroup.setSizePolicy(sizePolicy)
        self.fileGroup.setTitle("")
        self.fileGroup.setObjectName("fileGroup")
        self.verticalLayoutWidget = QtGui.QWidget(self.fileGroup)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 601, 401))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.treeView = DirTreeView(self.verticalLayoutWidget)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancel = QtGui.QPushButton(self.verticalLayoutWidget)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout.addWidget(self.cancel)
        self.load = QtGui.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(13)
        font.setWeight(50)
        font.setItalic(False)
        font.setBold(False)
        self.load.setFont(font)
        self.load.setObjectName("load")
        self.horizontalLayout.addWidget(self.load)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(FileBrowserDialog)
        QtCore.QMetaObject.connectSlotsByName(FileBrowserDialog)

    def retranslateUi(self, FileBrowserDialog):
        FileBrowserDialog.setWindowTitle(QtGui.QApplication.translate("FileBrowserDialog", "File Browser", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("FileBrowserDialog", "Choose Files/Directories:", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("FileBrowserDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.load.setText(QtGui.QApplication.translate("FileBrowserDialog", "Load", None, QtGui.QApplication.UnicodeUTF8))

from custom_widgets import DirTreeView
