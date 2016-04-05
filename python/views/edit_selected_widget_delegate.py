# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .widget_delegate import WidgetDelegate

class EditSelectedWidgetDelegate(WidgetDelegate):
    """
    Custom delegate that provides a simple mechanism where an actual widget (editor) is 
    presented for the selected item whilst all other items are simply drawn with a single
    widget.

    :ivar selection_model:      The selection model of the delegate's parent view, if one
                                existed at the time of the delegate's initialization.
    :vartype selection_model:   QtGui.QItemSelectionModel

    You use this class by subclassing it and implementing the methods:

    - :meth:`_get_painter_widget()`     - return the widget to be used to paint an index
    - :meth:`_on_before_paint()`        - set up the widget with the specific data ready to be painted
    - :meth:`sizeHint()`                - return the size of the widget to be used in the view

    If you want to have an interactive widget (editor) for the selected item
    then you will also need to implement:
    
    - :meth:`_create_editor_widget()`   - return a unique editor instance to be used for editing
    - :meth:`_on_before_selection()`    - set up the widget with the specific data ready for 
      interaction

    .. note:: If you are using the same widget for all items then you can just implement 
              the :meth:`_create_widget()` method instead of the separate :meth:`_get_painter_widget()` 
              and :meth:`_create_editor_widget()` methods.

    .. note:: In order for this class to handle selection correctly, it needs to be 
              attached to the view *after* the model has been attached. (This is 
              to ensure that it is able to obtain the view's selection model correctly.)
    """
    def __init__(self, view):
        """
        :param view: The parent view for this delegate
        :type view:  :class:`~PySide.QtGui.QWidget`
        """
        WidgetDelegate.__init__(self, view)

        # tracks the currently active cell
        self.__current_editor_index = None

        # note! Need to have a model connected to the view in order
        # to have a selection model.
        self.selection_model = view.selectionModel()

        if self.selection_model:
            self.selection_model.selectionChanged.connect(self._on_selection_changed)

    ########################################################################################
    # implemented by deriving classes

    def _on_before_selection(self, widget, model_index, style_options):
        """
        This method is called just before a cell is selected. This method should 
        configure values on the widget (such as labels, thumbnails etc) based on the 
        data contained in the model index parameter which is being passed.

        :param widget: The QWidget (constructed in _create_widget()) which will 
                       be used to paint the cell. 
        :type parent:  :class:`~PySide.QtGui.QWidget`
        
        :param model_index: QModelIndex object representing the data of the object that is 
                            about to be drawn.
        :type model_index:  :class:`~PySide.QtCore.QModelIndex`
        
        :param style_options: object containing specifics about the 
                              view related state of the cell.
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`
        """
        pass

    ########################################################################################
    # 'private' methods that are not meant to be subclassed or called by a deriving class.

    def _on_selection_changed(self, selected, deselected):
        """
        Signal triggered when someone changes the selection in the view.

        :param selected:    A list of the indexes in the model that were selected
        :type selected:     :class:`~PySide.QtGui.QItemSelection`
        :param deselected:  A list of the indexes in the model that were deselected
        :type deselected:  :class:`~PySide.QtGui.QItemSelection`
        """
        # clean up        
        if self.__current_editor_index:
            self.parent().closePersistentEditor(self.__current_editor_index)
            self.__current_editor_index = None

        selected_indexes = selected.indexes()

        if len(selected_indexes) > 0:
            # get the currently selected model index
            model_index = selected_indexes[0]
            # create an editor widget that we use for the selected item
            self.__current_editor_index = model_index
            # this will trigger the call to createEditor
            self.parent().openPersistentEditor(model_index)

    def createEditor(self, parent_widget, style_options, model_index):
        """
        Subclassed implementation from QStyledItemDelegate which is
        called when an "editor" is set up - the editor is set up 
        via the openPersistentEditor call and is created upon selection
        of an item.

        Normally, for performance, when we draw hundreds of grid cells, 
        we use the same Qwidget as a brush and simply use it to paint.

        For the currently selected cell however, we need to be able to interact
        with the widget (e.g. click a button for example) and therefore we need
        to have a real widget for this.

        :param parent_widget:   The parent widget to use for the new editor widget
        :type parent_widget:    :class:`~PySide.QtGui.QWidget`
        
        :param style_options:   The style options to use when creating the editor
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`
        
        :param model_index:     The index in the data model that will be edited 
                                using this editor
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`
        
        :returns:               An editor widget that will be used to edit this 
                                index
        :rtype:                 :class:`~PySide.QtGui.QWidget`
        """
        # create the editor by calling the base method:
        editor_widget = WidgetDelegate.createEditor(self, parent_widget, style_options, model_index)

        # and set it up to operate on the index:
        self._on_before_selection(editor_widget, model_index, style_options)
        return editor_widget

    def paint(self, painter, style_options, model_index):
        """
        Paint method to handle all cells that are not being currently edited.

        :param painter:         The painter instance to use when painting
        
        :param style_options:   The style options to use when painting
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`
        
        :param model_index:     The index in the data model that needs to be painted
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`
        """
        if model_index == self.__current_editor_index:
            # avoid painting the index twice!
            return
        WidgetDelegate.paint(self, painter, style_options, model_index)

