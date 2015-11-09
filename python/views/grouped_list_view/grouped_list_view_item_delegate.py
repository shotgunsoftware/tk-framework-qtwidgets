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
Custom item delegate for use with the GroupedListView
"""

import sgtk
from sgtk.platform.qt import QtGui, QtCore

from ..widget_delegate import WidgetDelegate
from .group_widget import GroupWidget

class GroupedListViewItemDelegate(WidgetDelegate):
    """
    Base delegate class for a delegate specifically to be used by a :class:`GroupedListView`.

    The delegate provides a method to return a group widget in addition to the regular
    delegate methods.
    """
    
    def __init__(self, view):
        """
        :param view: The view this delegate is operating on
        :type view:  :class:`~PySide.QtGui.QWidget`
        """
        WidgetDelegate.__init__(self, view)

        self._calc_group_widget = None

    def create_group_widget(self, parent):
        """
        Create a group header widget for the grouped list view

        :param parent:  The parent QWidget to use for the new group widget
        :type parent:   :class:`~PySide.QtGui.QWidget`
        :returns:       A widget derived from GroupWidgetBase that will
                        be used for a group in the grouped list view
        :rtype:         :class:`GroupWidgetBase`
        """
        # base implementation just returns the default group widget
        return GroupWidget(parent)

    def sizeHint(self, style_options, model_index):
        """
        Overriden base method returns the size hint for the specified model index

        :param style_options:   The style options to use when determining the size
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`
        
        :param model_index:     The index in the model to return the size hint for
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`
        
        :returns:               The QSize representing the size for the index in the view
        :rtype:                 :class:`~PySide.QtCore.QSize`
        """
        if model_index.parent() == self.view.rootIndex():
            # the index is a root/group item:

            # get the expanded state of this group in the view:
            expanded = self.view.is_expanded(model_index)

            # we use a single group widget to track the size:
            # (TODO) - this won't work if different group widgets
            # are created for different groups!
            if not self._calc_group_widget:
                self._calc_group_widget = self.create_group_widget(self.view)
                self._calc_group_widget.setVisible(False)

            # update the widget and return the size:
            self._calc_group_widget.set_expanded(expanded)
            self._calc_group_widget.set_item(model_index)
            layout = self._calc_group_widget.layout()
            if layout:
                # this ensures the widget is updated correctly 
                # using it's internal layout
                layout.invalidate()
                layout.activate()

            return self._calc_group_widget.sizeHint()
        else:
            # return the base size hint:
            return WidgetDelegate.sizeHint(self, style_options, model_index)

