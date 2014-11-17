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

# load resources
from .ui import resources_rc

from .shotgun_overlay_widget import ShotgunOverlayWidget

class ShotgunModelOverlayWidget(ShotgunOverlayWidget):
    """
    """
    
    def __init__(self, model, parent=None):
        """
        """
        ShotgunOverlayWidget.__init__(self, parent)
        
        # connect up to signals being emitted from Shotgun model:
        self._model = None
        self._connect_to_model(model)
        
    def set_model(self, model):
        """
        """
        self.hide()
        self._connect_to_model(model)

    def _connect_to_model(self, model):
        """
        """
        if model == self._model:
            return
        
        if self._model:
            self._model.query_changed.disconnect(self._model_query_changed)
            self._model.data_refreshing.disconnect(self._model_refreshing)
            self._model.data_refreshed.disconnect(self._model_refreshed)
            self._model.data_refresh_fail.disconnect(self._model_refresh_failed)
            self._model = None
            self.hide(hide_errors=True)            
            
        if model:
            self._model = model
            self._model.query_changed.connect(self._model_query_changed)
            self._model.data_refreshing.connect(self._model_refreshing)
            self._model.data_refreshed.connect(self._model_refreshed)
            self._model.data_refresh_fail.connect(self._model_refresh_failed)
            
    def _model_query_changed(self):
        """
        """
        self.hide(hide_errors=True)
        
    def _model_refreshing(self):
        """
        """
        if not self._model.is_data_cached():
            self.start_spin()
    
    def _model_refreshed(self, data_changed):
        """
        """
        self.hide(hide_errors=True)
    
    def _model_refresh_failed(self, msg):
        """
        """
        self.show_error_message(msg)      