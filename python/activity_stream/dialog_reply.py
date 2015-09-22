    # Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui
from .ui.reply_dialog import Ui_ReplyDialog

class ReplyDialog(QtGui.QDialog):
    """
    Modal dialog that hosts a note reply widget.
    This is used when someone clicks on the reply button for a note.
    """
    
    def __init__(self, parent, data_retriever, note_id):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # first, call the base class and let it do its thing.
        QtGui.QDialog.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyDialog() 
        self.ui.setupUi(self)
        
        self.ui.note_widget.set_data_retriever(data_retriever)        
        self.ui.note_widget.data_updated.connect(self.close_after_create)
        self.ui.note_widget.close_clicked.connect(self.close_after_cancel)
        self.ui.note_widget.set_current_entity("Note", note_id)
        
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)        

        
    def close_after_create(self):
        self.setResult(QtGui.QDialog.Accepted)
        self.close()
        
    def close_after_cancel(self):
        self.setResult(QtGui.QDialog.Rejected)
        self.close()

    def showEvent(self, event):
        QtGui.QDialog.showEvent(self, event)
        self.ui.note_widget.open_editor()
    
    def closeEvent(self, event):
        self.ui.note_widget.destroy()
        # ok to close
        event.accept()
