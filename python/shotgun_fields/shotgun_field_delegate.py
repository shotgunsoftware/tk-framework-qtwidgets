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

views = sgtk.platform.current_bundle().import_module("views")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")


class ShotgunFieldDelegate(views.WidgetDelegate):
    """
    A delegate for a given type of Shotgun field.  This delegate is designed to work
    with indexes from a ShotgunModel where the value of the field is stored in the
    SG_ASSOCIATED_FIELD_ROLE role.
    """
    def __init__(self, sg_entity_type, field_name, display_class, editor_class, view, bg_task_manager=None):
        """
        Constructor

        :param sg_entity_type: Shotgun entity type
        :type sg_entity_type: String

        :param field_name: Shotgun field name
        :type field_name: String

        :param display_class: A shotgun field :class:`~PySide.QtGui.QWidget` to display the field info

        :param editor_class: A shotgun field :class:`~PySide.QtGui.QWidget` to edit the field info

        :param view: The parent view for this delegate
        :type view:  :class:`~PySide.QtGui.QWidget`
        """
        views.WidgetDelegate.__init__(self, view)

        self._entity_type = sg_entity_type
        self._field_name = field_name
        self._display_class = display_class
        self._editor_class = editor_class
        self._bg_task_manager = bg_task_manager

    def _create_widget(self, parent):
        """
        :param parent:  QWidget to parent the widget to
        :type parent:   :class:`~PySide.QtGui.QWidget`

        :returns:       QWidget that will be used to paint grid cells in the view.
        :rtype:         :class:`~PySide.QtGui.QWidget`
        """
        widget = self._display_class(
            parent=parent,
            entity_type=self._entity_type,
            field_name=self._field_name,
            bg_task_manager=self._bg_task_manager,
            delegate=True,
        )
        return widget

    def sizeHint(self, style_options, model_index):
        """
        Returns a size hint for the painter widget.
        """
        if not model_index.isValid():
            return QtCore.QSize()

        size_hint = QtCore.QSize()
        painter_widget = self._get_painter_widget(model_index, self.view)
        if painter_widget:
            size_hint = painter_widget.size()

        return size_hint

    def _create_editor_widget(self, model_index, style_options, parent):
        """
        :param model_index:     The index of the item in the model to return a widget for
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`

        :param style_options:   Specifies the current Qt style options for this index
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`

        :param parent:          The parent view that the widget should be parented to
        :type parent:           :class:`~PySide.QtGui.QWidget`

        :returns:               A QWidget to be used for editing the current index
        :rtype:                 :class:`~PySide.QtGui.QWidget`
        """
        if not model_index.isValid():
            return None

        if not self._editor_class:
            return None

        widget = self._editor_class(
            parent=parent,
            entity_type=self._entity_type,
            field_name=self._field_name,
            bg_task_manager=self._bg_task_manager,
            delegate=True,
        )
        return widget

    def _on_before_paint(self, widget, model_index, style_options):
        """
        Update the display widget with the value stored in the index's
        SG_ASSOCIATED_FIELD_ROLE role.

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

    #def setEditorData(self, widget, index):
    #    value = index.data(shotgun_model.ShotgunModel.SG_ASSOCIATED_FIELD_ROLE)
    #    sanitized_value = shotgun_model.sanitize_qt(value)
    #    widget.set_value(sanitized_value)

    def setModelData(self, editor, model, index):
        return editor.get_value()

    #def editorEvent(self, event, model, option, index):
    #    return True

def _display_value(widget, model_index):

    src_index = map_to_source(model_index)
    if not src_index or not src_index.isValid():
        widget._display_default()
        return

    if widget._field_name == "image":
        primary_item = src_index.model().item(src_index.row(), 0)
        icon = primary_item.icon()
        if icon:
            widget._display_value(icon.pixmap(QtCore.QSize(256, 256)))
            return

    value = src_index.data(shotgun_model.ShotgunModel.SG_ASSOCIATED_FIELD_ROLE)
    sanitized_value = shotgun_model.sanitize_qt(value)
    if sanitized_value is None:
        widget._display_default()
    else:
        widget._display_value(sanitized_value)

def map_to_source(idx, recursive=True):
    """
    Map the specified index to it's source model.  This can be done recursively to map
    back through a chain of proxy models to the source model at the beginning of the chain
    :param idx:         The index to map from
    :param recursive:   If true then the function will recurse up the model chain until it
                        finds an index belonging to a model that doesn't derive from
                        QAbstractProxyModel.  If false then it will just return the index
                        from the imediate parent model.
    :returns:           QModelIndex in the source model or the first model in the chain that
                        isn't a proxy model if recursive is True.
    """
    src_idx = idx
    while src_idx.isValid() and isinstance(src_idx.model(), QtGui.QAbstractProxyModel):
        src_idx = src_idx.model().mapToSource(src_idx)
        if not recursive:
            break
    return src_idx

