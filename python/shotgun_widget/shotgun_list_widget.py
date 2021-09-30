# Copyright (c) 2020 Shotgun Software Inc.
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
from tank.util import sgre as re

from .shotgun_widget import ShotgunWidget
from .ui.shotgun_list_widget import Ui_ShotgunListWidget

utils = sgtk.platform.current_bundle().import_module("utils")


class ShotgunListWidget(ShotgunWidget):
    """
    This Shotgun Widget is typically used in a list view mode.
    """

    def __init__(self, parent=None):
        """
        Class constructor

        :param parent: The parent widget
        """

        ShotgunWidget.__init__(self, parent)

        self._top_left = None
        self._top_right = None
        self._body = None

        # set up the UI
        self._ui = Ui_ShotgunListWidget()
        self._ui.setupUi(self)

        # Menu management
        self._ui.button.setMenu(self._menu)
        self._ui.button.setVisible(False)

    def set_formatting(self, top_left=None, top_right=None, body=None, thumbnail=True):
        """
        Set the rendering of the widget items.

        :param top_left:  Content to display in the top left area of the item
        :param top_right: Content to display in the top right area of the item
        :param body:      Content to display in the main area of the item
        :param thumbnail: If True, the widget will display a thumbnail. If False, no thumbnail will be displayed.
        """

        self._top_left = top_left
        self._top_right = top_right
        self._body = body

        self._thumbnail = thumbnail
        if not thumbnail:
            self._ui.thumbnail.setVisible(False)

    def set_text(self, sg_data):
        """
        Fill the widget items by replacing the tokens with the right values.

        :param sg_data: Dictionary of Shotgun data we want to use to replace the tokens with.
        """

        self._ui.left_corner.setText(
            utils.convert_token_string(self._top_left, sg_data)
        )
        self._ui.right_corner.setText(
            utils.convert_token_string(self._top_right, sg_data)
        )
        self._ui.body.setText(utils.convert_token_string(self._body, sg_data))

    def replace_extra_key(self, key_name, key_value):
        """
        Replace a non-Shotgun token by its value.

        :param key_name:  Name of the token to replace. It must be declared using <> character (eg <NODE>)
        :param key_value: Replacement value to use
        """

        def _replace_text(name, value, text):
            pattern = "{{<{pattern}>}}".format(pattern=name)
            # be sure to escape \ character to avoid having KeyError
            value = value.replace("\\", "\\\\")
            text = re.sub(pattern, r"{}".format(value), text)
            return text

        self._ui.left_corner.setText(
            _replace_text(key_name, key_value, self._ui.left_corner.text())
        )
        self._ui.right_corner.setText(
            _replace_text(key_name, key_value, self._ui.right_corner.text())
        )
        self._ui.body.setText(_replace_text(key_name, key_value, self._ui.body.text()))

    def clear(self, thumbnail=None):
        """
        Clear the widget values.

        :param thumbnail: If a thumbnail is supplied, it will be used as the "empty" thumbnail view
        """

        # Remove the text
        self._ui.left_corner.setText("")
        self._ui.right_corner.setText("")
        self._ui.body.setText("")

        if not self._thumbnail:
            return

        self.set_thumbnail(thumbnail)

    @staticmethod
    def calculate_size():
        """
        Calculates and returns a suitable size for this widget.

        :returns: Size of the widget
        """
        return QtCore.QSize(200, 102)
