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
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .shotgun_field_meta import ShotgunFieldMeta

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")


class ImageWidget(QtGui.QLabel):
    """
    Inherited from a :class:`~PySide.QtGui.QLabel`, this class is able to
    display an image field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _FIELD_TYPE = "image"

    def setup_widget(self):
        """
        Initialize the widget state.  Start up a Shotgun data retriever to download
        images in the background.
        """
        self._pixmap = None

        # start up a data retriever to fetch the thumbnail in the background
        self._data_retriever = shotgun_data.ShotgunDataRetriever(bg_task_manager=self._bg_task_manager)
        self._data_retriever.start()
        self._data_retriever.work_completed.connect(self._on_worker_signal)
        self._data_retriever.work_failure.connect(self._on_worker_failure)

    def _display_default(self):
        """ Default widget state is empty. """
        self.clear()

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
            thumbnail = data["image"]
            pixmap = QtGui.QPixmap.fromImage(thumbnail)
            self.setPixmap(pixmap)

    def _on_worker_failure(self, uid, msg):
        """
        On failure just display an error and set the toolkit to the error string.
        """
        if uid == self._task_uid:
            self.clear()
            self._pixmap = None
            self.setText("Error")
            self.setToolTip(msg)

    # preserve aspect ratio
    def setPixmap(self, pixmap):
        """
        Override the default implementation to keep around the pixmap so we can scale it as needed to preserve
        its aspect ratio.
        """
        self._pixmap = pixmap
        QtGui.QLabel.setPixmap(
            self,
            self._pixmap.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )

    def heightForWidth(self, width):
        """
        Override the default implementation to return the appropriate height once we scale
        the pixmap to preserve its aspect ratio.
        """
        if self._pixmap:
            ratio = float(width) / self._pixmap.width()
            return ratio * self._pixmap.height()

        return QtGui.QtLabel.heightForWidth(self, width)

    def sizeHint(self):
        """
        Override the default implementation to return the appropriate height for the pixmap
        once it has been scaled to preserve its aspect ratio.
        """
        if self._pixmap:
            w = self.width()
            return QtCore.QSize(w, self.heightForWidth(w))

        return QtGui.QLabel.sizeHint(self)

    def resizeEvent(self, event):
        """
        Override the default implementation to resize the pixmap while preserving its
        aspect ratio.
        """
        if self._pixmap:
            QtGui.QLabel.setPixmap(
                self,
                self._pixmap.scaled(
                    self.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
            )
        else:
            QtGui.QLabel.resizeEvent(self, event)
