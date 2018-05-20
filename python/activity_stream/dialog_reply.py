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
    
    def __init__(self, parent, bg_task_manager, note_id=None, allow_screenshots=True):
        """
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        :param bg_task_manager: Task manager to use to fetch sg data.
        :type  bg_task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager`
        :param note_id: The entity id number of the Note entity being replied to.
        :type  note_id: :class:`int`
        :param allow_screenshots: Boolean to allow or disallow screenshots, defaults to True.
        :type  allow_screenshots: :class:`Boolean`
        """        
        # first, call the base class and let it do its thing.
        QtGui.QDialog.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ReplyDialog() 
        self.ui.setupUi(self)

        self._note_id = note_id
        
        self.ui.note_widget.set_bg_task_manager(bg_task_manager)        
        self.ui.note_widget.data_updated.connect(self.close_after_create)
        self.ui.note_widget.close_clicked.connect(self.close_after_cancel)
        self.ui.note_widget.set_current_entity("Note", note_id)
        self.ui.note_widget.allow_screenshots(allow_screenshots)
        
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)

    @property
    def note_widget(self):
        """
        Returns the underlying :class:`~note_input_widget.NoteInputWidget`.
        """
        return self.ui.note_widget

    def _get_note_id(self):
        """
        Gets the entity id number for the parent Note entity
        being replied to.

        :returns:   int
        """
        return self._note_id

    def _set_note_id(self, note_id):
        """
        Sets the entity id number for the parent Note entity
        being replied to.

        :param note_id: Integer id of a Note entity in Shotgun.
        """
        self.ui.note_widget.set_current_entity("Note", note_id)
        self._note_id = note_id

    note_id = QtCore.Property(int, _get_note_id, _set_note_id)
        
    def close_after_create(self):
        """
        Callback called after successful reply
        """ 
        self.setResult(QtGui.QDialog.Accepted)
        self.close()
        
    def close_after_cancel(self):
        """
        Callback called after cancel
        """
        self.setResult(QtGui.QDialog.Rejected)
        self.close()

    def showEvent(self, event):
        QtGui.QDialog.showEvent(self, event)
        self.ui.note_widget.open_editor()
    
    def closeEvent(self, event):
        self.ui.note_widget.clear()
        # ok to close
        event.accept()

    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.
        
        :param task_manager: Background task manager to use
        :type task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager` 
        """
        self.ui.note_widget.set_bg_task_manager(task_manager)