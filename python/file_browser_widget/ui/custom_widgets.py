from tank.platform.qt import QtGui, QtCore

class DirTreeView(QtGui.QTreeView):
    
    def __init__(self, parent=None):
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
        if dirs_only:
            self.model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        else:
            self.model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries)
            
            
    def set_single_selection(self, single_selection):
        if single_selection:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        else:
            self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)


class SortProxyModel(QtGui.QSortFilterProxyModel):
    
    def __init__(self, parent=None):
        super(SortProxyModel, self).__init__(parent)
        self.setDynamicSortFilter(True)