# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform.qt import QtCore, QtGui
from .ui.file_browser import Ui_FileBrowserDialog


class FileBrowserDialog(QtGui.QDialog):
    """
    This class is a custom File Browser that allows selection of both directories and files
    unlike the native browsers.  When files/dirs are selected and the Load button is pushed,
    the filesSelected signal is emitted.  Otherwise, if Cancel is pressed, the rejected
    signal is emitted.
    """
    
    # signal is emitted when files have been selected and Load button has been pushed
    # returns a list of file paths (which can include directories)
    filesSelected = QtCore.Signal(list)
    
    def __init__(self):
        """
        Initializes the file browser ui and connects the signals for the two push button widgets.
        """
        QtGui.QDialog.__init__(self)

        # set up the UI
        self.ui = Ui_FileBrowserDialog()
        self.ui.setupUi(self)

        self.ui.load.clicked.connect(self._on_file_load)
        self.ui.cancel.clicked.connect(self._on_cancel)
        
        
    def set_directories_only(self, dirs_only):
        """
        In the event that you want to use this UI to only allow a user to choose a directory,
        this function can be used to toggle between files and directories or directories only.
        
        :param dirs_only: a bool indicating whether the user wants directories only
        """
        self.ui.treeView.set_directories_only(dirs_only)
        
        
    def set_single_selection(self, single_selection):
        """
        By default this widget allows for multiple selection, but if you want a user to only be
        able to choose a single file or directory, this function can be used.
        
        :param single_selection: a bool describing whether single selection is on or off
        """
        self.ui.treeView.set_single_selection(single_selection)
        
        
    def reset(self):
        """
        Collapses the tree back to the root level.  Useful if you're using the same instance for
        multiple browsing cases.
        """
        self.ui.treeView.collapseAll()
        root = self.ui.treeView.model.index(0,0)
        self.ui.treeView.setExpanded(root, True)


    def _on_file_load(self):
        """
        Executes when the load button is pressed, selected indexes are converted into a path list
        that are emitted to the user via the filesSelected signal and widget is closed.
        """
        selected_indexes = self.ui.treeView.selectedIndexes()
        file_paths = []
        for index in selected_indexes:
            if index.column() == 0:
                file_paths.append(self.ui.treeView.model.filePath(index))

        self.filesSelected.emit(file_paths)
        self.close()

    
    def _on_cancel(self):
        """
        Executes when the cancel button is pressed, rejected signal is emitted and widget is closed.
        """
        self.rejected.emit()
        self.close()
