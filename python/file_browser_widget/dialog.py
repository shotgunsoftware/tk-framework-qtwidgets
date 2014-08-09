# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from tank.platform.qt import QtCore, QtGui
from .ui.file_browser import Ui_FileBrowserDialog


class FileBrowserDialog(QtGui.QDialog):
    
    files_returned = QtCore.Signal(list)
    
    def __init__(self):
        QtGui.QDialog.__init__(self)

        # set up the UI
        self.ui = Ui_FileBrowserDialog()
        self.ui.setupUi(self)

        self.ui.load.clicked.connect(self._on_file_load)
        self.ui.cancel.clicked.connect(self.deleteLater)
    # end __init__

    def _on_file_load(self):
        selected_indexes = self.ui.treeView.selectedIndexes()
        file_paths = []
        for index in selected_indexes:
            if index.column() == 0:
                file_paths.append(self.ui.treeView.model.filePath(index))
            # end if
        # end for

        self.files_returned.emit(file_paths)
        self.deleteLater()
    # end _on_file_load

# end FileBrowserDialog
