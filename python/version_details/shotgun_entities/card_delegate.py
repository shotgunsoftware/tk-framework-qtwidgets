# Copyright (c) 2016 Shotgun Software Inc.
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
from .card_widget import ShotgunEntityCardWidget

views = sgtk.platform.current_bundle().import_module("views")
shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_model",
)

class ShotgunEntityCardDelegate(views.EditSelectedWidgetDelegate):
    """
    A delegate wrapper for :class:`~ShotgunEntityCardWidget`.

    :ivar show_labels:              Whether to show labels for any Shotgun
                                    fields displayed.
    :vartype show_labels:           bool

    :ivar label_exempt_fields:      A list of fields that are never to have a
                                    label, even if show_labels is True.
    :vartype label_exempt_fields:   [str, ...]

    :ivar show_border:              Whether to draw borders around card widgets
                                    that are not selected.
    :vartype show_border:           bool
    """

    def __init__(self, view, shotgun_field_manager=None, **kwargs):
        """
        Constructs a new ShotgunEntityCardDelegate.

        :param view:                    The parent view for this delegate.
        :type view:                     :class:`~QtGui.QAbstractItemView`
        :param shotgun_field_manager:   An optional :class:`~ShotgunFieldManager`
                                        to pass to any constructed widgets.
        :type shotgun_field_manager:    :class:`~ShotgunFieldManager`
        """
        super(ShotgunEntityCardDelegate, self).__init__(view)

        self._fields = ["code", "entity"]
        self._widget_cache = dict()
        self._shotgun_field_manager = shotgun_field_manager
        self.__current_editor = None

        self.show_labels = True
        self.label_exempt_fields = []
        self.show_border = True

    ##########################################################################
    # properties

    def _get_fields(self):
        """
        A list of fields being displayed by the delegate.
        """
        return self._fields

    def _set_fields(self, fields):
        self._fields = list(fields)

        # Force a reselection to rebuild any editor widgets since that
        # will also need to reflect the change in fields being displayed.
        if self.__current_editor:
            self.force_reselection()

    fields = property(_get_fields, _set_fields)

    @property
    def widget_cache(self):
        """
        A dictionary containing all painter widgets, keyed by model index.
        """
        return self._widget_cache

    ##########################################################################
    # public methods

    def add_field(self, field):
        """
        Adds the given field to the list of fields to display for the entity.

        :param field:   The name of the Shotgun field to add to the delegate.
        """
        if field not in self.fields:
            self._fields.append(field)

        # If it appears that we have a editor live at the moment
        # then we need to force a reselection to rebuild that
        # editor at the correct size, taking into account the
        # change in fields.
        if self.__current_editor:
            self.force_reselection()

    def force_reselection(self):
        """
        Forces a reselection of all currently-selected indexes. This serves
        the purpose of forcing a refresh of any active edit widgets.
        """
        selection = self.view.selectionModel().selection()
        self.view.selectionModel().clearSelection()
        QtGui.QApplication.processEvents()
        self.view.selectionModel().select(selection, QtGui.QItemSelectionModel.Select)

    def remove_field(self, field):
        """
        Removes the given field from the list of fields to display for the entity.

        :param field:   The name of the Shotgun field to remove from the delegate.
        """
        self.fields = [f for f in self.fields if f != field]

        # If it appears that we have a editor live at the moment
        # then we need to force a reselection to rebuild that
        # editor at the correct size, taking into account the
        # change in fields.
        if self.__current_editor:
            self.force_reselection()

    ##########################################################################
    # overridden methods

    def _create_widget(self, parent, editable=False):
        """
        Returns the widget to be used when creating items.

        :param parent:QWidget to parent the widget to
        :type parent: :class:`~PySide.QtGui.QWidget`
        :param bool editable: Whether the widget is to be created using editable
                              Shotgun fields widgets or not.
        
        :returns: QWidget that will be used to paint grid cells in the view.
        :rtype: :class:`~PySide.QtGui.QWidget` 
        """
        widget = ShotgunEntityCardWidget(
            parent=parent,
            shotgun_field_manager=self._shotgun_field_manager,
            editable=editable,
        )

        widget.fields = self.fields
        widget.show_labels = self.show_labels
        widget.show_border = self.show_border
        widget.label_exempt_fields = self.label_exempt_fields

        return widget

    def _get_painter_widget(self, model_index, parent):
        """
        Constructs a widget to act as the basis for the paint event. If
        a widget has already been instantiated for this model index, that
        widget will be reused, otherwise a new widget will be instantiated
        and cached.

        :param model_index: The index of the item in the model to return a widget for
        :type model_index:  :class:`~PySide.QtCore.QModelIndex`
        :param parent:      The parent view that the widget should be parented to
        :type parent:       :class:`~PySide.QtGui.QWidget`
        :returns:           A QWidget to be used for painting the current index
        :rtype:             :class:`~PySide.QtGui.QWidget`
        """
        if model_index in self._widget_cache:
            widget = self._widget_cache[model_index]

            if sorted(self.fields) == sorted(widget.fields):
                return widget

        widget = self._create_widget(parent)
        self._widget_cache[model_index] = widget
        self.sizeHintChanged.emit(model_index)

        return widget

    def _create_editor_widget(self, model_index, style_options, parent):
        """
        Called when a cell is being edited.

        :param model_index:     The index of the item in the model to return a widget for
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`
        
        :param style_options:   Specifies the current Qt style options for this index
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`
        
        :param parent:          The parent view that the widget should be parented to
        :type parent:           :class:`~PySide.QtGui.QWidget`
        
        :returns:               A QWidget to be used for editing the current index
        :rtype:                 :class:`~PySide.QtGui.QWidget`
        """
        widget = self._create_widget(parent, editable=False)
        self._on_before_paint(widget, model_index, style_options)
        self.__current_editor = (model_index, widget)
        return widget

    def _on_before_paint(self, widget, model_index, style_options):
        """
        Called when a cell is being painted.

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
        # Get the shotgun query data for this model item.     
        sg_item = shotgun_model.get_sg_data(model_index)
        widget.entity = sg_item

        if model_index in self.selection_model.selectedIndexes():
            widget.set_selected(True)
        else:
            widget.set_selected(False)

    ##########################################################################
    # sizing

    def sizeHint(self, style_options, model_index):
        """
        Base the size on the number of entity fields to be displayed. This
        number will affect the height component of the size hint.

        :param style_options:   Specifies the current Qt style options for this index.
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`

        :param model_index:     The index of the item in the model.
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`
        """
        # We have to do this ourselves instead of calling
        # _get_painter_widget because that itself emits
        # the sizeHintChanged signal, which would put us
        # into an infinite loop.
        widget = self._widget_cache.get(model_index) or self._create_widget(self.view)
        return widget.sizeHint()


