# Copyright (c) 2015 Shotgun Software Inc.
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
from .shotgun_field_manager import ShotgunFieldManager

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")


class ThumbnailWidget(QtGui.QLabel):
    def __init__(self, parent=None, value=None, bg_task_manager=None, **kwargs):
        QtGui.QLabel.__init__(self, parent, **kwargs)
        self._pixmap = None

        self._data_retriever = shotgun_data.ShotgunDataRetriever(bg_task_manager=bg_task_manager)
        self._data_retriever.start()
        self._data_retriever.work_completed.connect(self._on_worker_signal)
        self._data_retriever.work_failure.connect(self._on_worker_failure)

        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.clear()
            return

        self._task_uid = self._data_retriever.request_thumbnail(
                value,  # url must still be valid since we don't know the entity this is for
                None,   # unknown entity_type
                None,   # unknown entity_id
                None,   # unknown field
            )

    def _on_worker_signal(self, uid, request_type, data):
        if uid == self._task_uid:
            pixmap = QtGui.QPixmap(data["thumb_path"])
            self.setPixmap(pixmap)

    def _on_worker_failure(self, uid, msg):
        if uid == self._task_uid:
            self.clear()
            self._pixmap = None
            self.setText("Error")
            self.setToolTip(msg)

    # preserve aspect ratio
    def setPixmap(self, pixmap):
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
        if self._pixmap:
            ratio = float(width) / self._pixmap.width()
            return ratio * self._pixmap.height()

        return QtGui.QtLabel.heightForWidth(self, width)

    def sizeHint(self):
        if self._pixmap:
            w = self.width()
            return QtCore.QSize(w, self.heightForWidth(w))

        return QtGui.QLabel.sizeHint(self)

    def resizeEvent(self, event):
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

ShotgunFieldManager.register("image", ThumbnailWidget)
