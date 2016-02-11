# Copyright (c) 2015 Shotgun Software Inc.
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
from .shotgun_field_manager import ShotgunFieldManager

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")


class ImageWidget(QtGui.QLabel):
    """
    Inherited from a :class:`~PySide.QtGui.QLabel`, this class is able to
    display an image field value as returned by the Shotgun API.
    """

    def __init__(self, parent=None, value=None, bg_task_manager=None, **kwargs):
        """
        Constructor for the widget.  This method passes all keyword args except
        for those below through to the :class:`~PySide.QtGui.QLabel` it
        subclasses.

        :param parent: Parent widget
        :type parent: :class:`PySide.QtGui.QWidget`

        :param value: The initial value displayed by the widget as described by set_value

        :param bg_task_manager: The task manager the widget will use if it needs to run a task
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        QtGui.QLabel.__init__(self, parent, **kwargs)
        self._pixmap = None

        # start up a data retriever to fetch the thumbnail in the background
        self._data_retriever = shotgun_data.ShotgunDataRetriever(bg_task_manager=bg_task_manager)
        self._data_retriever.start()
        self._data_retriever.work_completed.connect(self._on_worker_signal)
        self._data_retriever.work_failure.connect(self._on_worker_failure)

        self.set_value(value)

    def set_value(self, value):
        """
        Set the value displayed by the widget.

        :param value: The value displayed by the widget
        :type value: A String that is a valid URL for the thumbnail image
        """
        if value is None:
            self.clear()
            return

        # queue up the download in the background
        self._task_uid = self._data_retriever.request_thumbnail(
                value,  # url must still be valid since we don't know the entity this is for
                None,   # unknown entity_type
                None,   # unknown entity_id
                None,   # unknown field
            )

    def _on_worker_signal(self, uid, request_type, data):
        """
        Handle the finished download by updating the image the label displays.
        """
        if uid == self._task_uid:
            pixmap = QtGui.QPixmap(data["thumb_path"])
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

ShotgunFieldManager.register("image", ImageWidget)
