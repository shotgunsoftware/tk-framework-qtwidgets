from tank.platform.qt import QtGui, QtCore

class DirTreeView(QtGui.QTreeView):
    def __init__(self, parent=None):
        super(DirTreeView, self).__init__(parent)
        
        # set up file system model
        self.model = QtGui.QFileSystemModel()
        # don't show . and .. directories
        self.model.setFilter(\
            QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries)
        self.model.setRootPath("/")

        self.setModel(self.model)

        root = self.model.index(0,0)
        self.setRootIndex(root)

        # configure view
        self.setExpanded(root, True)
        self.setColumnWidth(0, 400)
        self.setColumnHidden(2, True)
        self.setExpandsOnDoubleClick(False)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)


class SortProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(SortProxyModel, self).__init__(parent)
        self.setDynamicSortFilter(True)