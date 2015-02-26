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

from ..views.widget_delegate import WidgetDelegate as WidgetDelegateBase

class WidgetDelegate(WidgetDelegateBase):
    """
    Custom delegate that provides a simple mechanism where an actual widget (editor) is 
    presented for the selected item whilst all other items are simply drawn with a single
    widget.
        
    This class can be used in conjunction with the various widgets found as part of the 
    framework module (for example list_widget and thumb_widget).
    
    You use this class by subclassing it and implementing the methods:
    
    - _get_painter_widget()     - return the widget to be used to paint an index
    - _on_before_paint()        - set up the widget with the specific data ready to be painted
    - sizeHint()                - return the size of the widget to be used in the view
    
    If you want to have an interactive widget (editor) for the selected item
    then you will also need to implement:
    - _create_editor_widget()   - return a unique editor instance to be used for editing
    - _on_before_selection()    - set up the widget with the specific data ready for 
                                  interaction

    If you are using the same widget for all items then you can just implement this method
    instead of the separate _get_painter_widget() & _create_editor_widget() methods
    - _create_widget()          - create a widget to be used for both painting and editing 
                                  of all items
    
    Note! In order for this class to handle selection correctly, it needs to be 
    attached to the view *after* the model has been attached. (This is to ensure that it 
    is able to obtain the view's selection model correctly.)
    """
    def __init__(self, view):
        """
        Constructor

        :param view:                        The parent view for this delegate
        :param edit_on_selection_changed:   If set to True then an interactive editor will 
                                            be created for the selected item as soon as the 
                                            item is selected. 
                                            Note that the view must be initialised with the 
                                            model before creation of this delegate for this 
                                            to work correctly!
        """
        WidgetDelegateBase.__init__(self, view)

        # tracks the currently active cell
        self.__current_editor_index = None    
        
        # note! Need to have a model connected to the view in order
        # to have a selection model.
        self.__selection_model = view.selectionModel()
        if self.__selection_model:
            self.__selection_model.selectionChanged.connect(self._on_selection_changed)
        
    ########################################################################################
    # implemented by deriving classes
            
    def _on_before_selection(self, widget, model_index, style_options):
        """
        This method is called just before a cell is selected. This method should 
        configure values on the widget (such as labels, thumbnails etc) based on the 
        data contained in the model index parameter which is being passed.
        
        :param widget: The QWidget (constructed in _create_widget()) which will 
                       be used to paint the cell. 
        :param model_index: QModelIndex object representing the data of the object that is 
                            about to be drawn.
        :param style_options: QStyleOptionViewItem object containing specifics about the 
                              view related state of the cell.
        """
        pass        
        
    ########################################################################################
    # 'private' methods that are not meant to be subclassed or called by a deriving class.
        
    def _on_selection_changed(self, selected, deselected):
        """
        Signal triggered when someone changes the selection in the view.
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
        """
        # create the editor by calling the base method:
        editor_widget = WidgetDelegateBase.createEditor(self, parent_widget, style_options, model_index)
                
        # and set it up to operate on the index:
        self._on_before_selection(editor_widget, model_index, style_options)
        return editor_widget

    def paint(self, painter, style_options, model_index):
        """
        Paint method to handle all cells that are not being currently edited.

        :param painter:         The painter instance to use when painting
        :param style_options:   The style options to use when painting
        :param model_index:     The index in the data model that needs to be painted
        """        
        if model_index == self.__current_editor_index:
            return
        WidgetDelegateBase.paint(self, painter, style_options, model_index)

