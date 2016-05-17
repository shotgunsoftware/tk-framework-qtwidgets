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

from .label_base_widget import ElidedLabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

from .ui import resources_rc


class FileLinkWidget(ElidedLabelBaseWidget):

    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "url"
    _EDITOR_TYPE = "url"

    def enable_editing(self, enable):
        self._editable = enable
        self._update_btn_position()

    def eventFilter(self, obj, event):

        if obj == self and self._editable:
            if event.type() == QtCore.QEvent.Enter:
                self._update_btn_position()
                self._popup_btn.show()
            elif event.type() == QtCore.QEvent.Leave:
                self._popup_btn.hide()

        return False

    def setup_widget(self):
        """
        Initialize the widget state.
        """

        self._editable = False

        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred
        )

        self._popup_btn = QtGui.QPushButton(self)
        self._popup_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/link_menu.png"))
        self._popup_btn.setFixedSize(QtCore.QSize(18, 12))
        self._popup_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self._popup_btn.hide()

        # make sure there's never a bg color or border
        self._popup_btn.setStyleSheet("background-color: none; border: none;")

        # XXX implement all the actions

        # actions
        self._upload_action = QtGui.QAction("Upload File", self)
        self._upload_action.triggered.connect(self._upload_file)

        self._link_action = QtGui.QAction("Link to Web Page", self)
        #self._link_action.triggered.connect(self._link_file)

        self._local_action = QtGui.QAction("Link to Local File or Directory", self)
        #self._local_action.triggered.connect(self._link_local)

        self._replace_with_upload_action = QtGui.QAction("Replace with Uploaded File", self)
        self._replace_with_upload_action.triggered.connect(self._upload_file)

        self._replace_with_link_action = QtGui.QAction("Replace with Web Page Link", self)
        #self._replace_with_link_action.triggered.connect(self._link_file)

        self._replace_with_local_action = QtGui.QAction("Replace with Local File or Directory", self)
        #self._replace_with_local_action.triggered.connect(self._link_file)

        self._clear_contents_action = QtGui.QAction("Remove File/Link", self)
        #self._clear_contents_action.triggered.connect(self._clear_contents)

        self._edit_link_action = QtGui.QAction("Edit Web Page Link", self)
        #self._edit_link_action.triggered.connect(self._edit_link)

        self.installEventFilter(self)

        self._display_default()
        self._update_btn_position()

        # ---- connect signals

        self._popup_btn.clicked.connect(self._on_popup_btn_click)
        self.linkActivated.connect(self._on_link_activated)

    def _display_default(self):
        self.clear()

    def _on_link_activated(self, url):
        QtGui.QDesktopServices.openUrl(url)

    def _on_popup_btn_click(self):

        popup_menu = QtGui.QMenu()

        # XXX introspect self._value dict

        if self._local_file:
            popup_menu.addAction(self._replace_with_upload_action)
            popup_menu.addAction(self._replace_with_link_action)
            popup_menu.addAction(self._replace_with_local_action)
            popup_menu.addAction(self._clear_contents_action)
        elif self._link_url:
            popup_menu.addAction(self._replace_with_upload_action)
            popup_menu.addAction(self._edit_link_action)
            popup_menu.addAction(self._replace_with_local_action)
            popup_menu.addAction(self._clear_contents_action)
        else:
            popup_menu.addAction(self._upload_action)
            popup_menu.addAction(self._link_action)
            popup_menu.addAction(self._local_action)

        popup_menu.exec_(
            self._popup_btn.mapToGlobal(
                QtCore.QPoint(0, self._popup_btn.height())
            )
        )

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A dictionary as returned by the Shotgun API for a url field
        """

        link_color = sgtk.constants.SG_STYLESHEET_CONSTANTS["SG_HIGHLIGHT_COLOR"]

        if value["link_type"] in ["web", "upload"]:
            url = value["url"]
            str_val = value.get("name", url)
            str_val = "<a href='%s'><font color='%s'>%s</font></a>" % (
                url, link_color, str_val)
        elif value["link_type"] == "local":
            local_path = value["local_path"]
            # for file on OS that differs from the current OS, this will
            # result in the display of the full path rather than just the
            # file basename.ext (the SG behavior).
            file_name = os.path.split(local_path)[-1]
            str_val = "<a href='file:///%s'><font color='%s'>%s</font></a>" % (
                local_path, link_color, file_name)

        return str_val

    def _update_btn_position(self):
        x = self.line_width + 4
        visible_width = self.visibleRegion().boundingRect().width()
        if (x + self._popup_btn.width()) > visible_width:
            x = self.visibleRegion().boundingRect().width() - self._popup_btn.width()
        self._popup_btn.move(x, -2)

    def _upload_file(self):

        file_path = QtGui.QFileDialog.getOpenFileName(
            self,
            caption="Replace Image",
            options=QtGui.QFileDialog.DontResolveSymlinks,
        )[0]
        if file_path and os.path.exists(file_path):
            self._clear()

            # populte dict to match SG value
            self.set_value({
                # XXX
            })

