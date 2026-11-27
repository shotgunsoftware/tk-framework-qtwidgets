# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import tempfile
import shutil
import sys

from tank.platform.qt import QtCore, QtGui
import tank

shotgun_data = tank.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_data"
)

from .ui.item import Ui_Item
from .list_base import ListBase


class ListItem(ListBase):
    def __init__(self, app, worker, parent=None):
        ListBase.__init__(self, app, worker, parent)

        self._selected = False
        self._worker = worker
        self._worker_uid = None
        self._connected_to_worker = False

        # spinner
        self._spin_icons = []
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/thumb_loading_1.png")
        )
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/thumb_loading_2.png")
        )
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/thumb_loading_3.png")
        )
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/thumb_loading_4.png")
        )

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_spinner)
        self._current_spinner_index = 0

        # set up styles for selected/unselected states
        self._unselected_style = {
            "border-radius": "2px",
            "border-style": "solid",
            "border-width": "1px",
            "border-color": "rgba(0,0,0,48)",
            "background-color": "rgba(0,0,0,48)",
        }
        self._selected_style = self._unselected_style.copy()
        self._selected_style["background-color"] = "rgb(112, 112, 112)"
        self._selected_style["border-color"] = "rgb(112, 112, 112)"

        self.set_selected(False)

    def supports_selection(self):
        return True

    def set_selected(self, status):
        self._selected = status
        ss = self._style_as_string(
            "#background",
            [self._unselected_style, self._selected_style][self._selected],
        )
        self.ui.background.setStyleSheet(ss)

    def is_selected(self):
        return self._selected

    def set_details(self, txt):
        self.ui.details.setText(txt)

    def get_details(self):
        return self.ui.details.text()

    def set_thumbnail(self, url):

        if url.startswith("http"):
            # start spinning
            self._timer.start(100)

            if not self._connected_to_worker:
                # make sure we are connected to the worker before we start work
                # otherwise we might miss the completed/failure signal!
                self._connected_to_worker = True
                self._worker.notifier.work_completed.connect(
                    self._on_worker_task_complete
                )
                self._worker.notifier.work_failure.connect(self._on_worker_failure)

            # queue job to download the thumbnail:
            self._worker_uid = self._worker.queue_work(
                self._download_thumbnail, {"url": url}
            )
        else:
            # assume url is a path on disk or resource
            self.ui.thumbnail.setPixmap(QtGui.QPixmap(url))

    ############################################################################################
    # internal stuff

    def _setup_ui(self):
        """
        Setup the Qt UI.  Typically, this just instantiates the UI class
        and calls its .setupUi(self) method.

        :returns:    The constructed QWidget
        """
        ui = Ui_Item()
        ui.setupUi(self)
        return ui

    def _style_as_string(self, name, style_dict):
        style_elements = ["%s: %s;" % (key, value) for key, value in style_dict.items()]
        return "%s { %s }" % (name, "".join(style_elements))

    def _update_spinner(self):
        """
        Animate spinner icon
        """
        self.ui.thumbnail.setPixmap(self._spin_icons[self._current_spinner_index])
        self._current_spinner_index += 1
        if self._current_spinner_index == 4:
            self._current_spinner_index = 0

    def _download_thumbnail(self, data):
        """
        Download a thumbnail into the standard  Toolkit thumbnail cache

        :param data:    Dictionary that should contain a 'url' key, the value of which is the url of
                        the thumbnail to download.
        :returns:       A dictionary containing a 'thumb_path' key, the value of which is the path
                        to the cached thumbnail
        """
        url = data["url"]

        path_to_cached_thumb = None
        try:
            path_to_cached_thumb = shotgun_data.ShotgunDataRetriever.download_thumbnail(
                url, self._app
            )
        except Exception as e:
            self._app.log_info(
                "Could not get thumbnail for url '%s'. Error: %s" % (url, e)
            )
            path_to_cached_thumb = None

        return {"thumb_path": path_to_cached_thumb}

    def _on_worker_task_complete(self, uid, data):
        if uid != self._worker_uid:
            return

        # stop spin
        self._timer.stop()

        # set thumbnail!
        try:
            path = data.get("thumb_path")
            self.ui.thumbnail.setPixmap(QtGui.QPixmap(path))
        except:
            self.ui.thumbnail.setPixmap(
                QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/thumb_empty.png")
            )

    def _on_worker_failure(self, uid, msg):

        if self._worker_uid != uid:
            # not our job. ignore
            return

        # stop spin
        self._timer.stop()

        # show error message
        self._app.log_warning("Worker error: %s" % msg)
