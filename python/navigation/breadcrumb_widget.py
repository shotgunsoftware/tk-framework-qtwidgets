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
Breadcrumb widget that displays a list of breadcrumbs.  This is currently
just a glorified label but could be extended later to support more
interaction/features if needed.
"""

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.breadcrumb_widget import Ui_BreadcrumbWidget

class Breadcrumb(object):
    """
    Base breadcrumb class that all breadcrumb instances 
    should be derived from
    """
    def __init__(self, label):
        """
        Construction

        :param label:   The label for this breadcrumb
        """
        self._label = label

    @property
    def label(self):
        """
        :returns:   The label for this breadcrumb
        """
        return self._label

class BreadcrumbWidget(QtGui.QWidget):
    """
    Implementation of the BreadcrumbWidget class
    """
    def __init__(self, parent=None):
        """
        :param parent:   The parent QWidget for this control
        :type parent:    :class:`~PySide.QtGui.QWidget`
        """
        QtGui.QWidget.__init__(self, parent)

        # set up the UI
        self._ui = Ui_BreadcrumbWidget()
        self._ui.setupUi(self)

        self._ui.path_label.elide_mode = QtCore.Qt.ElideLeft
        self._ui.path_label.setText("")

    def set(self, breadcrumbs):
        """
        Populate the breadcrumb control with a list of breadcrumbs

        :param breadcrumbs: A list of breadcrumbs.  Each breadcrumb instance should derive 
                            from the Breadcrumb class
        :type breadcrumbs: list of :class:`Breadcrumb`
        """
        # build a single path from the list of crumbs:
        path = "<span style='color:#2C93E2'> &#9656; </span>".join([crumb.label for crumb in breadcrumbs])
        path = "<big>%s</big>" % path

        # and update the label:
        self._ui.path_label.setText(path)
