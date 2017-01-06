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

# ensures access to `link_menu.png`
from .ui import resources_rc


class FileLinkWidget(ElidedLabelBaseWidget):
    """
    Display a ``url`` field value as returned by the Shotgun API.

    The ``FileLinkWidget`` represents both the ``DISPLAY`` and ``EDITOR`` widget type.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "url"
    _EDITOR_TYPE = "url"

    def enable_editing(self, enable):
        """
        Enable or disable editing of the widget.

        This is provided as required for widgets that are used as both editor
        and display.

        :param bool enable: ``True`` to enable, ``False`` to disable
        """
        self._editable = enable
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

        if obj == self and self._editable:
            if event.type() == QtCore.QEvent.Enter:
                self._update_btn_position()
                self._popup_btn.show()
            elif event.type() == QtCore.QEvent.Leave:
                self._popup_btn.hide()

        return False

    def setup_widget(self):
        """
        Prepare the widget for display.

        Called by the metaclass during initialization.
        """

        self._editable = False

        self._popup_btn = QtGui.QPushButton(self)
        self._popup_btn.setIcon(QtGui.QIcon(":/qtwidgets-shotgun-fields/link_menu.png"))
        self._popup_btn.setFixedSize(QtCore.QSize(18, 12))
        self._popup_btn.hide()

        if not self._delegate:
            # not sure why, but when the widget is being used in a delegate,
            # this causes editor to close immediately when clicked.
            self._popup_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        # make sure there's never a bg color or border
        self._popup_btn.setStyleSheet("background-color: none; border: none;")

        # ---- actions

        # each of the different types use the same callback, but they display
        # different text depending on the current value

        # upload
        self._upload_file_action = QtGui.QAction("Upload File", self)
        self._upload_file_action.triggered.connect(self._upload_file)

        self._edit_upload_file_action = QtGui.QAction("Upload New File", self)
        self._edit_upload_file_action.triggered.connect(self._upload_file)

        self._replace_with_upload_file_action = QtGui.QAction("Replace with Uploaded File", self)
        self._replace_with_upload_file_action.triggered.connect(self._upload_file)

        # web
        self._web_page_link_action = QtGui.QAction("Link to Web Page", self)
        self._web_page_link_action.triggered.connect(self._edit_link)

        self._edit_web_page_link_action = QtGui.QAction("Edit Web Page Link", self)
        self._edit_web_page_link_action.triggered.connect(self._edit_link)

        self._replace_with_web_page_link_action = QtGui.QAction("Replace with Web Page Link", self)
        self._replace_with_web_page_link_action.triggered.connect(self._edit_link)

        # local
        self._local_path_action = QtGui.QAction("Link to Local File or Directory", self)
        self._local_path_action.triggered.connect(self._browse_local)

        self._edit_local_path_action = QtGui.QAction("Edit Local File or Directory", self)
        self._edit_local_path_action.triggered.connect(self._browse_local)

        self._replace_with_local_path_action = QtGui.QAction("Replace with Local File or Directory", self)
        self._replace_with_local_path_action.triggered.connect(self._browse_local)

        # remove
        self._remove_link_action = QtGui.QAction("Remove File/Link", self)
        self._remove_link_action.triggered.connect(self._remove_link)

        self.installEventFilter(self)

        self._display_default()
        self._update_btn_position()

        # ---- connect signals

        self._popup_btn.clicked.connect(self._on_popup_btn_click)
        self.linkActivated.connect(self._on_link_activated)

    def _browse_local(self):
        """
        Opens a file browser for choosing a local file for the field.

        If a file is selected, this method emits the ``value_changed`` signal
        and upates the stored value.
        """

        # prompt the user for a file. this always returns a tuple, the second
        # value being the path (or None)
        file_path = QtGui.QFileDialog.getOpenFileName(
            self,
            caption="Link to Local File or Directory",
            options=QtGui.QFileDialog.DontResolveSymlinks,
        )[0]

        # make sure we have a valid path
        if not file_path or not os.path.exists(file_path):
            return

        self.clear()
        file_path = str(file_path)

        # emit the value changed signal. build a fake value for now that
        # will presumably be updated via calling code
        self._value = {
            "name": os.path.split(file_path)[-1],
            "link_type": "local",
            "url": None,
            "local_path": file_path,
        }
        self._display_value(self._value)
        self.value_changed.emit()

    def _display_default(self):
        """
        Display the default value of the widget.
        """
        self.clear()

    def _edit_link(self):
        """
        Opens a custom dialog for the user to input a url and display name.
        """

        url = None
        display = None

        # get the current url and display if the current link is a web link
        if self._value and self._value["link_type"] == "web":
            url = self._value.get("url", None)
            display = self._value.get("name", None)

        # prompt the user
        edit_link_dialog = _EditWebLinkDialog(self, url, display)
        result = edit_link_dialog.exec_()

        if result == QtGui.QDialog.Rejected:
            return

        self.clear()

        # emit the value changed signal. build a fake value for now that
        # will presumably be updated via calling code
        self._value = {
            "name": edit_link_dialog.display,
            "link_type": "web",
            "url": edit_link_dialog.url,
        }
        self._display_value(self._value)
        self.value_changed.emit()

    def _on_link_activated(self, url):
        """
        Open the displayed link in an appropriate way.

        Called when a user clicks the link.

        :param url: The url for the clicked link.
        """

        if self._value:
            link_type = self._value["link_type"]
        else:
            link_type = None

        if self._value.get("link_type") == "upload":
            # the uploaded urls have timeouts built in. query the current
            # value before continuing
            sg = self._bundle.shotgun
            result = sg.find_one(
                self._entity["type"],
                [['id', 'is', self._entity["id"]]],
                [self._field_name],
            )
            if not result:
                return
            url = result[self._field_name]["url"]

            # SG returns an encoded url already. make sure it doesn't get
            # a second encoding pass (the default translation from python str
            # to QUrl seems to assume the str is not encoded).
            url = QtCore.QUrl.fromEncoded(url)

        # display the url appropriately
        if url:
            QtGui.QDesktopServices.openUrl(url)

    def _on_popup_btn_click(self):
        """
        Display a context menu based on the current field value.
        """

        popup_menu = QtGui.QMenu()

        if self._value:
            link_type = self._value["link_type"]
        else:
            link_type = None

        if not link_type:
            # no link type, display options for each type
            popup_menu.addAction(self._upload_file_action)
            popup_menu.addAction(self._web_page_link_action)
            popup_menu.addAction(self._local_path_action)
        elif link_type == "upload":
            popup_menu.addAction(self._edit_upload_file_action)
            popup_menu.addAction(self._replace_with_web_page_link_action)
            popup_menu.addAction(self._replace_with_local_path_action)
            popup_menu.addAction(self._remove_link_action)
        elif link_type == "web":
            popup_menu.addAction(self._replace_with_upload_file_action)
            popup_menu.addAction(self._edit_web_page_link_action)
            popup_menu.addAction(self._replace_with_local_path_action)
            popup_menu.addAction(self._remove_link_action)
        elif link_type == "local":
            popup_menu.addAction(self._replace_with_upload_file_action)
            popup_menu.addAction(self._replace_with_web_page_link_action)
            popup_menu.addAction(self._edit_local_path_action)
            popup_menu.addAction(self._remove_link_action)

        # show the menu below the button
        popup_menu.exec_(
            self._popup_btn.mapToGlobal(
                QtCore.QPoint(0, self._popup_btn.height())
            )
        )

    def _remove_link(self):
        """
        Called when user selects the menu option to clear the value.
        """

        # clear the value of the field, emit the ``value_changed`` signal.
        self.clear()
        self._value = {
            "name": None,
            "link_type": None,
            "url": None,
        }
        self._display_value(self._value)
        self.value_changed.emit()

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A dictionary as returned by the Shotgun API for a url field
        """
        utils = self._bundle.import_module("utils")
        if value["link_type"] in ["web", "upload"]:
            url = value["url"]
            img_src = ":/qtwidgets-shotgun-fields/link_%s.png" % (value["link_type"],)
            hyperlink = utils.get_hyperlink_html(url, value.get("name", url))
            str_val = "<span><img src='%s'>&nbsp;%s</span>" % (img_src, hyperlink)
        elif value["link_type"] == "local":
            local_path = value["local_path"]
            # for file on OS that differs from the current OS, this will
            # result in the display of the full path rather than just the
            # file basename.ext (the SG behavior).
            file_name = os.path.split(local_path)[-1]
            img_src = ":/qtwidgets-shotgun-fields/link_%s.png" % (value["link_type"],)
            hyperlink = utils.get_hyperlink_html(local_path, file_name)
            str_val = "<span><img src='%s'>&nbsp;%s</span>" % (img_src, hyperlink)
        else:
            str_val = ""

        return str_val

    def _update_btn_position(self):
        """
        Ensures the menu button is displayed properly in relation to the label text.
        """
        # `line_width` is the elided width of the line in pixels. use this as a
        # starting point for where to place the menu button
        x = self.line_width + 4

        # if the label is too wide, move the button inside the visible rectangle
        visible_width = self.visibleRegion().boundingRect().width()
        if (x + self._popup_btn.width()) > visible_width:
            x = self.visibleRegion().boundingRect().width() - self._popup_btn.width()
        self._popup_btn.move(x, -2)

    def _upload_file(self):
        """
        Opens a file browser for uploading a file for the field.

        If a file is selected, this method emits the ``value_changed`` signal
        and upates the stored value.
        """

        # prompt the user for a file. this always returns a tuple, the second
        # value being the path (or None)
        file_path = QtGui.QFileDialog.getOpenFileName(
            self,
            caption="Choose a File to Upload",
            options=QtGui.QFileDialog.DontResolveSymlinks,
        )[0]

        if not file_path or not os.path.exists(file_path):
            return

        self.clear()

        file_path = str(file_path)

        # emit the value changed signal. build a fake value for now that
        # will presumably be updated via calling code
        self._value = {
            "name": os.path.split(file_path)[-1],
            "link_type": "upload",
            "url": file_path,
        }
        self._display_value(self._value)
        self.value_changed.emit()


class _EditWebLinkDialog(QtGui.QDialog):
    """
    Class for prompting the user for link url and aname
    """

    def __init__(self, parent=None, url=None, display=None):
        """
        Initialize the dialog.

        :param parent: Optional parent widget
        :param url: Optional url to insert it the input
        :param display: Optional display name to
        :return:
        """

        super(_EditWebLinkDialog, self).__init__(parent)

        self.setMinimumWidth(350)

        url = url
        display= display

        self.setWindowTitle("Link to Web Page")

        # url input
        url_lbl = QtGui.QLabel("<h3>Web page address</h3>")
        self._url_input = QtGui.QLineEdit()
        if url:
            self._url_input.setText(url)
            self._url_input.selectAll()

        # display input
        display_lbl = QtGui.QLabel("Optional display name")
        self._display_input = QtGui.QLineEdit()
        if display:
            self._display_input.setText(display)
            self._display_input.selectAll()

        # get the highlight color
        btn_color = sgtk.platform.current_bundle().style_constants["SG_HIGHLIGHT_COLOR"]
        btn_palette = self.palette()
        btn_palette.setColor(QtGui.QPalette.Button, btn_color)

        # color the button to match the SG version.
        self._add_link_btn = QtGui.QPushButton("Add Link")
        self._add_link_btn.setEnabled(False)
        self._add_link_btn.setPalette(btn_palette)

        cancel_btn = QtGui.QPushButton("Cancel")

        # put the buttons together. Didn't user QDialogButtonBox since can't
        # control the order
        btn_box = QtGui.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(self._add_link_btn)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(url_lbl)
        layout.addWidget(self._url_input)
        layout.addWidget(display_lbl)
        layout.addWidget(self._display_input)
        layout.addLayout(btn_box)

        # signals
        self._url_input.textChanged.connect(self._check_url)
        self._add_link_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def _check_url(self, text):
        """
        Enable add link button if the url is valid, disable otherwise

        :param text: The typed text
        """

        url = QtCore.QUrl(text)
        self._add_link_btn.setEnabled(url.isValid())

    @property
    def url(self):
        """:obj:`str` url entered by the user."""
        return self._url_input.text()

    @property
    def display(self):
        """:obj:`str` display name entered by the user."""
        return self._display_input.text()

