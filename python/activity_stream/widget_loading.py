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

from .widget_activity_stream_base import ActivityStreamBaseWidget

from .ui.loading_widget import Ui_LoadingWidget


class LoadingWidget(ActivityStreamBaseWidget):
    """
    Widget that displays a "loading..." message in the activity stream.
    This is typically displayed while widgets updates are still 
    being loaded in.
    """
    
    def __init__(self, parent):
        """
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        # now load in the UI that was created in the UI designer
        self.ui = Ui_LoadingWidget() 
        self.ui.setupUi(self)


