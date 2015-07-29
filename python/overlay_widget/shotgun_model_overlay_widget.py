# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Overlay widget specifically designed to work with a shotgun model (from the 
tk-framework-shotgunutils framework).  Multiple overlay widgets can be
easily created and connected to the same shotgun model.
"""

from sgtk.platform.qt import QtCore, QtGui

# load resources
from .ui import resources_rc
from .shotgun_overlay_widget import ShotgunOverlayWidget

class ShotgunModelOverlayWidget(ShotgunOverlayWidget):
    """
    Overlay widget class
    """

    def __init__(self, sg_model, parent=None):
        """
        Construction

        :param sg_model:    Shotgun model that this widget should connect to
        :param parent:      The parent QWidget this widget should be parented to
        """
        ShotgunOverlayWidget.__init__(self, parent)

        # connect up to signals being emitted from Shotgun model:
        self._model = None
        self._connect_to_model(sg_model)

    def set_model(self, sg_model):
        """
        Set the model this widget should be connected to

        :param sg_model:    Shotgun model that this widget should connect to
        """
        self.hide()
        self._connect_to_model(sg_model)

    def _connect_to_model(self, sg_model):
        """
        Connect to the signals emitted by the specified model

        :param sg_model:    Shotgun model that this widget should connect to
        """
        if sg_model == self._model:
            # already connected!
            return

        if self._model:
            # disconnect from the previous model:
            self._model.query_changed.disconnect(self._model_query_changed)
            self._model.data_refreshing.disconnect(self._model_refreshing)
            self._model.data_refreshed.disconnect(self._model_refreshed)
            self._model.data_refresh_fail.disconnect(self._model_refresh_failed)
            self._model = None
            self.hide(hide_errors=True)

        if sg_model:
            # connect to the new model:
            self._model = sg_model
            self._model.query_changed.connect(self._model_query_changed)
            self._model.data_refreshing.connect(self._model_refreshing)
            self._model.data_refreshed.connect(self._model_refreshed)
            self._model.data_refresh_fail.connect(self._model_refresh_failed)

    def _model_query_changed(self):
        """
        Slot signalled when the query changes on the connected Shotgun model
        """
        self.hide(hide_errors=True)

    def _model_refreshing(self):
        """
        Slot signalled when the connected Shotgun model starts refreshing
        """
        if not self._model.is_data_cached():
            self.start_spin()

    def _model_refreshed(self, data_changed):
        """
        Slot signalled when the data from the connected Shotgun model has 
        been refreshed

        :param data_changed:    True if the refresh resulted in the data changing
        """
        self.hide(hide_errors=True)

    def _model_refresh_failed(self, msg):
        """
        Slot signalled when the connected Shotgun model refresh fails

        :param msg:    The reason the refresh failed
        """
        self.show_error_message(msg)


