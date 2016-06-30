# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .shotgun_field_meta import ShotgunFieldMeta

from .ui import resources_rc

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")


class ImageWidget(QtGui.QLabel):
    """
    Display an ``image`` field value as returned by the Shotgun API.

    The ``ImageWidget`` represents both the ``DISPLAY`` and ``EDITOR`` widget type.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "image"
    _EDITOR_TYPE = "image"

    @property
    def image_url(self):
        """
        The string url to the currently loaded image file.
        """
        return self._image_url

    def enable_editing(self, enable):
        """
        Enable or disable editing of the widget.

        This is provided as required for widgets that are used as both editor
        and display.

        :param bool enable: ``True`` to enable, ``False`` to disable
        """
        self._editable = enable
        self._update_display()
        self._update_btn_position()

    def eventFilter(self, obj, event):
        """
        Filters out mouse enter/leave events in order to show/hide the edit
        menu when the widget is editable.

        :param obj: The watched object.
        :type obj: :class:`~PySide.QtGui.QObject`
        :param event: The filtered event.
        :type event: :class:`~PySide.QtGui.QEvent`

        :return: True if the event was processed, False otherwise
        """

        if obj == self:
            if self._pixmap and event.type() == QtCore.QEvent.Enter:
                self._popup_btn.show()
            elif self._pixmap and event.type() == QtCore.QEvent.Leave:
                self._popup_btn.hide()

        return False

    def heightForWidth(self, width):
        """
        Override the default implementation to return the appropriate height
        once we scale the pixmap to preserve its aspect ratio.

        :param int width: The width of the pixmap
        :return: The calculated height
        """

        if self._pixmap:
            ratio = float(width) / self._pixmap.width()
            return ratio * self._pixmap.height()

        return super(ImageWidget, self).heightForWidth(width)

    def minimumSizeHint(self):
        """
        Override the default implementation to return a minimum size of
        ``QtCore.QSize(32, 32)``.
        """
        if self._pixmap:
            return QtCore.QSize(32, 32)
        else:
            return super(ImageWidget, self).minimumSizeHint()

    def resizeEvent(self, event):
        """
        Override the default implementation to resize the pixmap while preserving its
        aspect ratio.

        :param event: The resize event object.
        :type event: :class:`~PySide.QtGui.QResizeEvent`
        """
        if self._pixmap:
            self._scale_pixmap()
        else:
            super(ImageWidget, self).resizeEvent(event)

    def setPixmap(self, pixmap):
        """
        Override the default implementation to keep around the pixmap so we can
        scale it as needed to preserve its aspect ratio.

        :param pixmap: The pixmap to set as the current pixmap
        :type pixmap: :class:`~PySide.QtGui.QPixmap`
        """
        self._pixmap = pixmap
        self._scale_pixmap()

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """
        self._pixmap = None
        self._image_url = None
        self._editable = False
        self._scaled_width = self.width()

        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # start up a data retriever to fetch the thumbnail in the background
        self._data_retriever = shotgun_data.ShotgunDataRetriever(bg_task_manager=self._bg_task_manager)
        self._data_retriever.start()
        self._data_retriever.work_completed.connect(self._on_worker_signal)
        self._data_retriever.work_failure.connect(self._on_worker_failure)

        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding
        )

        # menu display button for showing the popup menu
        self._popup_btn = QtGui.QPushButton(self)
        self._popup_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/image_menu.png"))
        self._popup_btn.setFixedSize(QtCore.QSize(18, 12))
        self._popup_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self._popup_btn.hide()

        # make sure there's never a bg color or border
        self._popup_btn.setStyleSheet("background-color: none; border: none;")

        # actions
        self._clear_action = QtGui.QAction("Clear Thumbnail", self)
        self._clear_action.triggered.connect(self._clear_image)

        self._replace_action = QtGui.QAction("Replace Thumbnail", self)
        self._replace_action.triggered.connect(self._upload_image)

        self._view_action = QtGui.QAction("View Image", self)
        self._view_action.triggered.connect(self._show_image)

        self._popup_edit_menu = QtGui.QMenu()
        self._popup_edit_menu.addAction(self._clear_action)
        self._popup_edit_menu.addAction(self._replace_action)
        self._popup_edit_menu.addAction(self._view_action)

        self._popup_display_menu = QtGui.QMenu()
        self._popup_display_menu.addAction(self._view_action)

        self.installEventFilter(self)

        self._display_default()
        self._update_btn_position()

        # ---- connect signals

        self._popup_btn.clicked.connect(self._on_popup_btn_click)
        self.linkActivated.connect(self._on_link_activated)

    def sizeHint(self):
        """
        Override the default implementation to return the appropriate height for
        the pixmap once it has been scaled to preserve its aspect ratio.
        """

        if self._pixmap:
            w = self.width()
            return QtCore.QSize(w, self.heightForWidth(w))

        return super(ImageWidget, self).sizeHint()

    def _clear_image(self):
        """
        Clear the widget of the current image, displaying the default value.
        """
        self._display_default()
        self.value_changed.emit()

    def _display_default(self):
        """
        Display the default value of the widget.
        """
        self.clear()
        self._pixmap = None
        self._image_url = None
        self._update_display()

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value returned by the Shotgun API to be displayed
        """
        # queue up the download in the background
        entity_id = self._entity and self._entity.get("id") or None
        entity_type = self._entity and self._entity.get("type") or None
        self._task_uid = self._data_retriever.request_thumbnail(
            value, entity_type, entity_id, self._field_name, load_image=True)

    def _on_link_activated(self, url):
        """
        Handle a url being clicked in the widget display.

        :param url: The url being clicked on.
        :return:
        """
        if url.startswith("image::"):
            action = url.split("::")[-1]
            if action == "upload":
                # the url looks to be internal and signifies the request to upload
                # a new image
                self._upload_image()
        else:
            # not an internal url scheme. pass along to desktop services
            QtGui.QDesktopServices.openUrl(url)

    def _on_popup_btn_click(self):
        """
        Handles displaying the popup menu when the button is clicked.
        """

        if self._editable:
            menu = self._popup_edit_menu
        else:
            menu = self._popup_display_menu

        menu.exec_(
            self._popup_btn.mapToGlobal(
                QtCore.QPoint(0, self._popup_btn.height())
            )
        )

    def _on_worker_failure(self, uid, msg):
        """
        On failure just display an error and set the toolkit to the error string.
        """
        if uid == self._task_uid:
            self.clear()
            self.setText("Error loading image.")
            self.setToolTip(msg)

    def _on_worker_signal(self, uid, request_type, data):
        """
        Handle the finished download by updating the image the label displays.
        """
        if uid == self._task_uid:
            image = data["image"]
            self._image_url = data["thumb_path"]
            pixmap = QtGui.QPixmap.fromImage(image)
            self.setPixmap(pixmap)

    def _replace_image(self):
        """
        Replace the current image by prompting for a new one.
        """
        self._upload_image()

    def _scale_pixmap(self):
        """
        Scale the pixmap in preparation for display.
        """
        scaled_pixmap = self._pixmap.scaled(
            self.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self._scaled_width = scaled_pixmap.width()
        super(ImageWidget, self).setPixmap(scaled_pixmap)
        self._update_btn_position()

    def _show_image(self):
        """
        The user requested to show the file. Forward to desktop services.
        """
        QtGui.QDesktopServices.openUrl("file:///%s" % (self._image_url))

    def _update_btn_position(self):
        """
        Make sure the menu button is always displayed correctly in the scaled
        pixmap rect.
        """

        # accessing the pixmap() in this method when called form the
        # resizeEvent causes really weird things to happen. this is why we
        # store the scaled width/height
        if self._pixmap:
            self._popup_btn.move(self._scaled_width - self._popup_btn.width() - 2, 2)

    def _update_display(self):
        """
        If no pixmap, display a link to upload if the widget is editable,
        otherwise display a ``No Image`` string.
        """
        if not self._pixmap:
            if self._editable:
                # SG_LINK_COLOR is newer to core than the highlight color, so we'll
                # fall back on highlight if the explicit link color isn't available.
                style_constants = sgtk.platform.current_bundle().style_constants
                link_color = style_constants.get(
                    "SG_LINK_COLOR",
                    style_constants["SG_HIGHLIGHT_COLOR"],
                )
                self.setText(
                    "<a href='image::upload'><font color='%s'>Upload Image"
                    "</font></a>" % (link_color,)
                )
            else:
                self.setText("No Image")

    def _upload_image(self):
        """
        Display a file browser and process the selected file path.
        """

        file_path = QtGui.QFileDialog.getOpenFileName(
            self,
            caption="Replace Image",
            options=QtGui.QFileDialog.DontResolveSymlinks,
        )[0]
        if file_path:
            self.setPixmap(QtGui.QPixmap(file_path))
            self._image_url = file_path
            self.value_changed.emit()

