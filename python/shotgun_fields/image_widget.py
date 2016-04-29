# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Widget that represents the value of an image field in Shotgun
"""
import os

import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .shotgun_field_meta import ShotgunFieldMeta

from .ui import resources_rc

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")


class ImageWidget(QtGui.QLabel):
    """
    Inherited from a :class:`~PySide.QtGui.QLabel`, this class is able to
    display an image field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "image"
    _EDITOR_TYPE = "image"

    def setup_widget(self):
        """
        Initialize the widget state.  Start up a Shotgun data retriever to download
        images in the background.
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
            QtGui.QSizePolicy.Preferred
        )

        self._popup_btn = QtGui.QPushButton(self)
        self._popup_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/image_menu.png"))
        self._popup_btn.setFixedSize(QtCore.QSize(18, 12))
        self._popup_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self._popup_btn.hide()

        # actions
        self._clear_action = QtGui.QAction("Clear Thumbnail", self)
        self._clear_action.triggered.connect(self._clear_image)

        self._replace_action = QtGui.QAction("Replace Thumbnail", self)
        self._replace_action.triggered.connect(self._upload_image)

        self._view_action = QtGui.QAction("View Image", self)
        self._view_action.triggered.connect(self._show_image)

        self._popup_menu = QtGui.QMenu()
        #self._popup_menu.setLayoutDirection(QtCore.Qt.RightToLeft)
        self._popup_menu.addAction(self._clear_action)
        self._popup_menu.addAction(self._replace_action)
        self._popup_menu.addAction(self._view_action)

        # make sure there's never a bg color or border
        self._popup_btn.setStyleSheet("background-color: none; border: none;")

        self.installEventFilter(self)

        self._display_default()
        self._update_btn_position()

        # ---- connect signals

        self._popup_btn.clicked.connect(self._on_popup_btn_click)

        self.linkActivated.connect(self._on_link_activated)

    def _on_link_activated(self, url):

        if url.startswith("image::"):
            action = url.split("::")[-1]
            if action == "upload":
                self._upload_image()
        else:
            QtGui.QDesktopServices.openUrl(url)

    def _upload_image(self):

        file_path = QtGui.QFileDialog.getOpenFileName(
            self,
            caption="Replace Image",
            options=QtGui.QFileDialog.DontResolveSymlinks,
        )[0]
        if file_path and os.path.exists(file_path):
            # XXX may not want to replace immediately.
            # XXX update in SG first?
            self.setPixmap(QtGui.QPixmap(file_path))
            self._image_url = file_path
            self.value_changed.emit()

    def _on_popup_btn_click(self):

        self._popup_menu.exec_(
            self._popup_btn.mapToGlobal(
                QtCore.QPoint(0, self._popup_btn.height())
            )
        )

    def _clear_image(self):
        self._display_default()

    def _replace_image(self):
        self._upload_image()

    def _show_image(self):
        QtGui.QDesktopServices.openUrl("file:///%s" % (self._image_url))

    def enable_editing(self, enable):
        self._editable = enable
        self._update_display()
        self._update_btn_position()

    def _display_default(self):
        """ Default widget state is empty. """
        self.clear()
        self._pixmap = None
        self._image_url = None
        self._update_display()
        # XXX how will this work with SG uploads?
        self.value_changed.emit()

    def _update_display(self):
        if not self._pixmap:
            if self._editable:
                self.setText("<a href='image::upload'>Upload Image</a>")
            else:
                self.setText("No Image")

    def _display_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value displayed by the widget
        :type value: A String that is a valid URL for the thumbnail image
        """
        # queue up the download in the background
        entity_id = self._entity and self._entity.get("id") or None
        entity_type = self._entity and self._entity.get("type") or None
        self._task_uid = self._data_retriever.request_thumbnail(
            value, entity_type, entity_id, self._field_name, load_image=True)

    def _on_worker_signal(self, uid, request_type, data):
        """
        Handle the finished download by updating the image the label displays.
        """
        if uid == self._task_uid:
            image = data["image"]
            self._image_url = data["thumb_path"]
            pixmap = QtGui.QPixmap.fromImage(image)
            self.setPixmap(pixmap)

    def _on_worker_failure(self, uid, msg):
        """
        On failure just display an error and set the toolkit to the error string.
        """
        if uid == self._task_uid:
            self.clear()
            self.setText("Error loading image.")
            self.setToolTip(msg)

    # preserve aspect ratio
    def setPixmap(self, pixmap):
        """
        Override the default implementation to keep around the pixmap so we can scale it as needed to preserve
        its aspect ratio.
        """
        self._pixmap = pixmap
        self._scale_pixmap()

    def heightForWidth(self, width):
        """
        Override the default implementation to return the appropriate height once we scale
        the pixmap to preserve its aspect ratio.
        """
        if self._pixmap:
            ratio = float(width) / self._pixmap.width()
            return ratio * self._pixmap.height()

        return super(ImageWidget, self).heightForWidth(width)

    def minimumSizeHint(self):

        if self._pixmap:
            return QtCore.QSize(32, 32)
        else:
            return super(ImageWidget, self).minimumSizeHint()

    def sizeHint(self):
        """
        Override the default implementation to return the appropriate height for the pixmap
        once it has been scaled to preserve its aspect ratio.
        """

        if self._pixmap:
            w = self.width()
            return QtCore.QSize(w, self.heightForWidth(w))

        return super(ImageWidget, self).sizeHint()

    def resizeEvent(self, event):
        """
        Override the default implementation to resize the pixmap while preserving its
        aspect ratio.
        """

        if self._pixmap:
            self._scale_pixmap()
        else:
            super(ImageWidget, self).resizeEvent(event)

    def _scale_pixmap(self):
        scaled_pixmap = self._pixmap.scaled(
            self.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self._scaled_width = scaled_pixmap.width()
        super(ImageWidget, self).setPixmap(scaled_pixmap)
        self._update_btn_position()

    def eventFilter(self, obj, event):

        if obj == self and self._editable:
            if self._pixmap and event.type() == QtCore.QEvent.Enter:
                self._popup_btn.show()
            elif self._pixmap and event.type() == QtCore.QEvent.Leave:
                self._popup_btn.hide()

        return False

    def _update_btn_position(self):

        # accessing the pixmap() in this method when called form the
        # resizeEvent causes really weird things to happen. this is why we
        # store the scaled width/height
        if self._pixmap:
            self._popup_btn.move(self._scaled_width - self._popup_btn.width() - 2, 2)

