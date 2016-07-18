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
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
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

    def paint(self, painter, style_options, model_index):
        """
        Paint method to handle all cells that are not being currently edited.

        :param painter:         The painter instance to use when painting
        :param style_options:   The style options to use when painting
        :param model_index:     The index in the data model that needs to be painted
        """

        # let the base class do all the heavy lifting
        super(ShotgunFieldDelegate, self).paint(painter, style_options, model_index)

        # clear out the paint widget's contents to prevent it from showing in
        # other places in the view (since the widget is shared)
        widget = self._get_painter_widget(model_index, self.view)
        widget.set_value(None)

    def _create_widget(self, parent):
        """
        :param parent: QWidget to parent the widget to
        :type parent: :class:`~PySide.QtGui.QWidget`

        :returns: QWidget that will be used to paint grid cells in the view.
        :rtype: :class:`~PySide.QtGui.QWidget`
        """
        widget = self._display_class(
            parent=parent,
            entity_type=self._entity_type,
            field_name=self._field_name,
            bg_task_manager=self._bg_task_manager,
            delegate=True,
        )

        if self._display_class == self._editor_class:
            # display and edit classes are the same. we need to make sure
            # we disable the editing so that the delegate isn't drawn in its
            # edit state.
            widget.enable_editing(False)

        return widget

    def sizeHint(self, style_options, model_index):
        """
        Returns the size needed by the delegate to display the item specified by
        ``model_index``, taking into account the style information provided by
        ``style_options``.

        Reimplemented from ``QStyledItemDelegate.sizeHint``

        :param style_options: Style information for the item.
        :type style_options: :class:`~PySide.QtGui.QStyleOptionViewItem`
        :param model_index: The index of the item to return the size of.
        :type model_index: :class:`~PySide.QtCore.QModelIndex`

        :returns: size required by the delegate
        :rtype: :class:`~PySide.QtCore.QSize`
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
        Create an editor widget for the supplied model index.

        :param model_index: The index of the item in the model to return a widget for
        :type model_index: :class:`~PySide.QtCore.QModelIndex`

        :param style_options: Specifies the current Qt style options for this index
        :type style_options: :class:`~PySide.QtGui.QStyleOptionViewItem`

        :param parent: The parent view that the widget should be parented to
        :type parent: :class:`~PySide.QtGui.QWidget`

        :returns: A QWidget to be used for editing the current index
        :rtype: :class:`~PySide.QtGui.QWidget`
        """
        # ensure the field is editable
        if not shotgun_globals.field_is_editable(self._entity_type, self._field_name):
            return None

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

        if self._display_class == self._editor_class:
            # display and edit classes are the same. we need to make sure
            # we enable the editing
            widget.enable_editing(True)

        # auto fill the background color so that the display widget doesn't show
        # behind.
        widget.setAutoFillBackground(True)

        return widget

    def _on_before_paint(self, widget, model_index, style_options):
        """
        Update the display widget with the value stored in the index's
        SG_ASSOCIATED_FIELD_ROLE role.

        :param widget: The QWidget (constructed in _create_widget()) which will
            be used to paint the cell.
        :type parent: :class:`~PySide.QtGui.QWidget`

        :param model_index: object representing the data of the object that is
            about to be drawn.
        :type model_index: :class:`~PySide.QtCore.QModelIndex`

        :param style_options: Object containing specifics about the
            view related state of the cell.
        :type style_options: :class:`~PySide.QtGui.QStyleOptionViewItem`
        """

        # make sure the display widget is populated with the correct data
        _set_widget_value(widget, model_index)

    def setEditorData(self, editor, model_index):
        """
        Sets the data to be displayed and edited by the editor from the data
        model item specified by the model index.

        :param editor: The editor widget.
        :type editor: :class:`~PySide.QtGui.QWidget`
        :param model_index: The index of the model to be edited.
        :type model_index: :class:`~PySide.QtCore.QModelIndex`
        """

        # make sure the editor widget is populated with the correct data
        _set_widget_value(editor, model_index)

    def setModelData(self, editor, model, index):
        """
        Gets data from the editor widget and stores it in the specified model at the item index.

        :param editor: The editor widget.
        :type editor: :class:`~PySide.QtGui.QWidget`
        :param model: The SG model where the data lives.
        :type model: :class:`~shotgun_utils.shotgun_model.ShotgunModel`
        :param index: The index of the model to be edited.
        :type index: :class:`~PySide.QtCore.QModelIndex`
        """
        src_index = _map_to_source(index)
        if not src_index or not src_index.isValid():
            # invalide index, do nothing
            return

        new_value = editor.get_value()

        cur_value = src_index.data(shotgun_model.ShotgunModel.SG_ASSOCIATED_FIELD_ROLE)
        if cur_value == new_value:
            # value didn't change. nothing to do here.
            return

        bundle = sgtk.platform.current_bundle()

        # special case for image fields
        if editor._field_name == "image":
            primary_item = src_index.model().item(src_index.row(), 0)
            try:
                if new_value:
                    # update the value locally in the model
                    primary_item.setIcon(QtGui.QIcon(new_value))
                else:
                    primary_item.setIcon(QtGui.QIcon())
            except Exception, e:
                bundle.log_error("Unable to set icon for widget delegate: %s" % (e,))

            return

        successful = src_index.model().setData(
            src_index,
            new_value,
            shotgun_model.ShotgunModel.SG_ASSOCIATED_FIELD_ROLE,
        )

        if not successful:
            bundle.log_error(
                "Unable to set model data for widget delegate: %s, %s" %
                (self._entity_type, self._field_name)
            )

    def editorEvent(self, event, model, option, index):
        """
        Handles mouse events on the editor.

        :param event: The event that occurred.
        :type event: :class:`~PySide.QtCore.QEvent`
        :param model: The SG model where the data lives.
        :type model: :class:`~shotgun_utils.shotgun_model.ShotgunModel`
        :param option: Options for rendering the item.
        :type option: :class:`~PySide.QtQui.QStyleOptionViewItem`
        :param index: The index of the model to be edited.
        :type index: :class:`~PySide.QtCore.QModelIndex`

        :return: ``True``, if the event was handled, ``False`` otherwise.
        :rtype: ``bool``
        """

        # Forward mouse clicks to the underlying display widget. This only kicks
        # in if the editor widget isn't displayed or doesn't process a mouse
        # event for some reason. If you're having trouble with editors
        # disappearing, it may be because they can't receive focus or aren't
        # handling a mouse click.
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self._forward_mouse_event(event, index)
            return True

        return False

    def _forward_mouse_event(self, mouse_event, index):
        """
        Forward the mouse event to the display widget to simulate
        interacting with the widget. This is necessary since the delegate only
        paints the widget in the view rather than being an actual widget
        instance.

        :param mouse_event: The event that occured on the delegate.
        :type mouse_event: :class:`~PySide.QtCore.QEvent`
        :param index: The model index that was acted on.
        :type index: :class:`~PySide.QtCore.QModelIndex`
        """

        # get the widget used to paint this index, populate it with the
        # value for this index
        widget = self._get_painter_widget(index, self.view)
        _set_widget_value(widget, index)

        item_rect = self.view.visualRect(index)

        # get the rect of the item in the view
        widget.resize(item_rect.size())

        # move the widget to 0, 0 so we know exactly where it is
        widget.move(0, 0)

        # map global mouse position to within item_rect
        view_pos = self.view.viewport().mapFromGlobal(QtGui.QCursor.pos())

        # calculate the offset from the item rect
        widget_x = view_pos.x() - item_rect.x()
        widget_y = view_pos.y() - item_rect.y()

        # forward the mouse event to the display widget
        forward_event = QtGui.QMouseEvent(
            mouse_event.type(),
            QtCore.QPoint(widget_x, widget_y),
            mouse_event.button(),
            mouse_event.buttons(),
            mouse_event.modifiers(),
        )
        QtGui.QApplication.sendEvent(widget, forward_event)


def _set_widget_value(widget, model_index):
    """
    Updates the supplied widget with data from the supplied model index.

    :param widget: The widget to set the value for
    :type parent: :class:`~PySide.QtGui.QWidget`
    :param model_index: The index of the model where the data comes from
    :type model_index: :class:`~PySide.QtCore.QModelIndex`
    """

    src_index = _map_to_source(model_index)
    if not src_index or not src_index.isValid():
        # invalid index, do nothing
        return

    # special case for image fields
    if widget._field_name == "image":
        primary_item = src_index.model().item(src_index.row(), 0)
        icon = primary_item.icon()
        if icon:
            widget.set_value(icon.pixmap(QtCore.QSize(256, 256)))

    value = src_index.data(shotgun_model.ShotgunModel.SG_ASSOCIATED_FIELD_ROLE)
    widget.set_value(shotgun_model.sanitize_qt(value))


def _map_to_source(idx, recursive=True):
    """
    Map the specified index to it's source model.  This can be done recursively to map
    back through a chain of proxy models to the source model at the beginning of the chain

    :param idx: The index to map from
    :param recursive: If true then the function will recurse up the model chain until it
        finds an index belonging to a model that doesn't derive from QAbstractProxyModel.
        If false then it will just return the index from the imediate parent model.

    :returns: QModelIndex in the source model or the first model in the chain that
        isn't a proxy model if recursive is True.
    """
    src_idx = idx
    while src_idx.isValid() and isinstance(src_idx.model(), QtGui.QAbstractProxyModel):
        src_idx = src_idx.model().mapToSource(src_idx)
        if not recursive:
            break
    return src_idx

