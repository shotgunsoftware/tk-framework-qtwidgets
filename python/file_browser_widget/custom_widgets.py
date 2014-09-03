# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform.qt import QtGui, QtCore

class DirTreeView(QtGui.QTreeView):
    """
    Overloaded base class of the file tree.  This uses a QFileSystemModel object to build the tree
    data, and also defines a couple of convenience functions for easier use.
    """
    
    def __init__(self, parent=None):
        """
        Initializes the Tree View object, defines the model and the root of the tree.  Also
        sets single selection and directories only off to begin with since that is likely the
        most common use case.
        """ 
        super(DirTreeView, self).__init__(parent)
        
        # set up file system model
        self.model = QtGui.QFileSystemModel()
        self.set_directories_only(False)
        self.model.setRootPath("/")

        self.setModel(self.model)

        root = self.model.index(0,0)
        self.setRootIndex(root)

        # configure view
        self.setExpanded(root, True)
        self.setColumnWidth(0, 400)
        self.setColumnHidden(2, True)
        self.setExpandsOnDoubleClick(False)
        self.set_single_selection(False)
        
        
    def set_directories_only(self, dirs_only):
        """
        Largely a convenience function so the user doesn't have to know/understand these settings.
        Allows an instance to be used in a directories only situation as well as files and
        directories.
        
        :param dirs_only: bool specifying whether the model displays directories only or files as
                          well
        """
        if dirs_only:
            self.model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        else:
            self.model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries)
            
            
    def set_single_selection(self, single_selection):
        """
        Largely a convenience function so the user doesn't have to know/understand these settings.
        Allows an instance to allow both multiple selection and single selection if needed.
        
        :param single_selection: bool specifying whether the selection mode is set to allow multiple
                                 selections or a single selection
        """
        if single_selection:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        else:
            self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
