# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import weakref

import sgtk
from sgtk.platform.qt import QtCore, QtGui

USING_PYQT = hasattr(QtCore, "QVariant")

class WidgetDelegate(QtGui.QStyledItemDelegate):
    """
    Convenience wrapper that makes it straight forward to use widgets inside of delegates.

    This class is basically an adapter which lets you connect a view (:class:`~PySide.QtGui.QAbstractItemView`) 
    with a :class:`~PySide.QtGui.QWidget` of choice. This widget is used to "paint" the view when it is being 
    rendered. When editing the item in the view, this class will create an editor widget
    as defined by the class.

    You use this class by subclassing it and implementing the methods:

    - :meth:`_get_painter_widget()` - return the widget to be used to paint an index
    - :meth:`_on_before_paint()` - set up the widget with the specific data ready to be painted
    - :meth:`~PySide.QtGui.QAbstractItemDelegate.sizeHint()` - return the size of the widget to be used in the view

    If you want to provide an editor using the same widgetry then implement the following:

    - :meth:`_create_editor_widget()` - return a unique editor instance to be used for editing
      the specific index - style options should be applied to the editor at this point.
    - :meth:`setEditorData()` - populate the editor with data from the model
    - :meth:`setModelData()` - apply the data from the editor back to the model

    .. note:: If you are using the same widget for all items then you can just implement 
              the :meth:`_create_widget()` method instead of the separate :meth:`_get_painter_widget()` 
              and :meth:`_create_editor_widget()` methods.
    
    """
    def __init__(self, view):
        """
        :param view: The parent view for this delegate
        :type view:  :class:`~PySide.QtGui.QWidget`
        """
        QtGui.QStyledItemDelegate.__init__(self, view)

        # for backwards compatibility or where there is a single paint widget for
        # all model indexes, keep track of it here.  We use a weakref to track the widget
        # as it will be parented to another widget which will take care of garbage collection
        # when needed
        self.__paint_widget = None

        # help the GC
        self.__editors = []

    @property
    def view(self):
        """
        Return the parent view of this delegate.  This is just a wrapper
        for returning ``self.parent()`` but makes calling code easier to read!

        :returns: The parent view this delegate was created for
        :rtype:   :class:`~PySide.QtGui.QWidget`
        """
        return self.parent()

    ########################################################################################
    # implemented by deriving classes

    def _get_painter_widget(self, model_index, parent):
        """
        Return a widget that can be used to paint the specified model index.  If this
        is implemented in derived classes then the derived class is responsible for
        the lifetime of the widget.

        :param model_index: The index of the item in the model to return a widget for
        :type model_index:  :class:`~PySide.QtCore.QModelIndex`
        :param parent:      The parent view that the widget should be parented to
        :type parent:       :class:`~PySide.QtGui.QWidget`
        :returns:           A QWidget to be used for painting the current index
        :rtype:             :class:`~PySide.QtGui.QWidget`
        """

        if not model_index.isValid():
            # if the index is invalid, no field widget will be useful for display
            # or editing.
            return None

        # the default implementation just uses the internal __paint_widget 
        # (creating it if needed) for backwards compatibility
        if not self.__paint_widget or not self.__paint_widget():
            paint_widget = self._create_widget(parent)
            if not paint_widget:
                return None
            self.__paint_widget = weakref.ref(paint_widget)
        return self.__paint_widget()

    def _create_editor_widget(self, model_index, style_options, parent):
        """
        Return a new editor widget for the specified model index.  The base class is
        responsible for the lifetime of the widget meaning that the derived class should
        release all handles to it.

        :param model_index:     The index of the item in the model to return a widget for
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`
        
        :param style_options:   Specifies the current Qt style options for this index
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`
        
        :param parent:          The parent view that the widget should be parented to
        :type parent:           :class:`~PySide.QtGui.QWidget`
        
        :returns:               A QWidget to be used for editing the current index
        :rtype:                 :class:`~PySide.QtGui.QWidget`
        """
        # the default implementation just calls _create_widget for backwards
        # compatibility.

        if not model_index.isValid():
            # if the index is invalid, no field widget will be useful for editing.
            return None

        return self._create_widget(parent)

    def _on_before_paint(self, widget, model_index, style_options):
        """
        This needs to be implemented by any deriving classes.

        This is called just before a cell is painted. This method should configure values
        on the widget (such as labels, thumbnails etc) based on the data contained
        in the model index parameter which is being passed.

        :param widget: The QWidget (constructed in _create_widget()) which will 
                       be used to paint the cell. 
        :type parent:  :class:`~PySide.QtGui.QWidget`
        
        :param model_index: object representing the data of the object that is 
                            about to be drawn.
        :type model_index:  :class:`~PySide.QtCore.QModelIndex`
        
        :param style_options: Object containing specifics about the 
                              view related state of the cell.
        :type style_options:  :class:`~PySide.QtGui.QStyleOptionViewItem`
        """
        raise NotImplementedError

    def _create_widget(self, parent):
        """
        This needs to be implemented by any deriving classes unless the separate
        methods :meth:`_get_painter_widget()` and :meth:`_create_editor_widget()` 
        are implemented instead.

        :param parent:  QWidget to parent the widget to
        :type parent:   :class:`~PySide.QtGui.QWidget`
        
        :returns:       QWidget that will be used to paint grid cells in the view.
        :rtype:         :class:`~PySide.QtGui.QWidget` 
        """
        return None

    ########################################################################################
    # 'private' methods that are not meant to be subclassed or called by a deriving class.

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

        :param style_options:   The style options to use when creating the editor
        :param model_index:     The index in the data model that will be edited
                                using this editor
        :returns:               An editor widget that will be used to edit this
                                index
        """
        # allow derived class to create the editor widget:
        editor_widget = self._create_editor_widget(model_index, style_options, parent_widget)
        if not editor_widget:
            return None

        # keep tabs on all editors to avoid garbage collection problems:
        # (TODO) confirm that this is necessary as this will lead to the persistance of
        # an editor widget for every selected item in the view!
        self.__editors.append(editor_widget)

        return editor_widget

    def updateEditorGeometry(self, editor_widget, style_options, model_index):        
        """
        Subclassed implementation which is typically called  whenever an editor 
        widget is set up and needs resizing.  This happens immediately after 
        creation and also for example if the grid element size is changing.

        :param editor_widget:   The editor that needs resizing/updating
        :param style_options:   The style options to use when editing the editor
        :param model_index:     The index in the data model that will be edited 
                                using this editor
        """
        editor_widget.setGeometry(style_options.rect)

    def paint(self, painter, style_options, model_index):
        """
        Paint method to handle all cells that are not being currently edited.

        :param painter:         The painter instance to use when painting
        :param style_options:   The style options to use when painting
        :param model_index:     The index in the data model that needs to be painted
        """

        # for performance reasons, we are not creating a widget every time
        # but merely moving the same widget around. 
        paint_widget = self._get_painter_widget(model_index, self.parent())
        if not paint_widget:
            # just paint using the base implementation:
            QtGui.QStyledItemDelegate.paint(self, painter, style_options, model_index)
            return

        # make sure that the widget that is just used for painting isn't visible otherwise
        # it'll appear in the wrong place!
        paint_widget.setVisible(False)

        # call out to have the widget set the right values            
        self._on_before_paint(paint_widget, model_index, style_options)

        # now paint!
        painter.save()
        try:
            paint_widget.resize(style_options.rect.size())
            painter.translate(style_options.rect.topLeft())
            # note that we set the render flags NOT to render the background of the widget
            # this makes it consistent with the way the editor widget is mounted inside 
            # each element upon hover.

            # WEIRD! It seems pyside and pyqt actually have different signatures for this method
            if USING_PYQT:
                # pyqt is using the flags parameter, which seems inconsistent with QT
                # http://pyqt.sourceforge.net/Docs/PyQt4/qwidget.html#render            
                paint_widget.render(painter, 
                                          QtCore.QPoint(0,0),
                                          QtGui.QRegion(),
                                          QtGui.QWidget.DrawChildren)
            else:
                # pyside is using the renderFlags parameter which seems correct
                paint_widget.render(painter, 
                                          QtCore.QPoint(0,0),
                                          renderFlags=QtGui.QWidget.DrawChildren)
        finally:
            painter.restore()
            


