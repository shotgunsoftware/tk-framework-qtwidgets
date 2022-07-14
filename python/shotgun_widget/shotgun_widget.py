# Copyright (c) 2020 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
A simple widget to display Shotgun information.
The information we want to display can be formatted using the following rules:

    {[preroll]shotgun.field.name|sg_field_name_fallback::directive[postroll]}

Basic Examples:

- {code}                         # simple format
- {sg_sequence.Sequence.code}    # deep links
- {artist|created_by}            # if artist is null, use created_by

Directives are also supported - these are used by the formatting logic
and include the following:

- {sg_sequence::showtype}        # will generate a link saying
                                 # 'Sequence ABC123' instead of just
                                 # 'ABC123' like it does by default
- {sg_sequence::nolink}          # no url link will be created

Optional pre/post roll - if a value is null, pre- and post-strings are
omitted from the final result. Examples of this syntax:

- {[Name: ]code}                 # If code is set, 'Name: xxx' will be
                                 # printed out, otherwise nothing.
- {[Name: ]code[<br>]}           # Same but with a post line break
"""

import sgtk
from sgtk.platform.qt import QtCore, QtGui

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils",
    "shotgun_globals",
)

logger = sgtk.platform.get_logger(__name__)


class ShotgunWidget(QtGui.QWidget):
    """
    Shotgun widget base class.
    """

    def __init__(self, parent=None):
        """
        Construction

        :param parent: The parent widget
        """
        QtGui.QWidget.__init__(self, parent)

        self._thumbnail = True
        self._sg_fields = []

        # compute hilight colors
        p = QtGui.QPalette()
        highlight_col = p.color(QtGui.QPalette.Active, QtGui.QPalette.Highlight)
        self._highlight_str = "rgb(%s, %s, %s)" % (
            highlight_col.red(),
            highlight_col.green(),
            highlight_col.blue(),
        )
        self._transp_highlight_str = "rgba(%s, %s, %s, 25%%)" % (
            highlight_col.red(),
            highlight_col.green(),
            highlight_col.blue(),
        )

        self._menu = QtGui.QMenu()
        self._actions = []

    def set_thumbnail(self, thumbnail):
        """
        Set the widget thumbnail. If the widget has been configured to display a thumbnail but no image has been
        supplied, a default picture will be displayed instead.

        :param thumbnail: The thumbnail as a QtGui.QIcon
        """

        if not self._thumbnail:
            return

        if not thumbnail:
            pixmap = QtGui.QPixmap(
                ":/tk-framework-qtwidgets/shotgun_widget/rect_512x400.png"
            )
        else:
            pixmap = thumbnail.pixmap(512)

        self.set_scaled_thumbnail(pixmap)
        self._ui.thumbnail.setVisible(True)

    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not

        :param selected: True if selected, false if not
        """
        if selected:
            self._ui.box.setStyleSheet(
                """#box {border-width: 2px;
                                                 border-color: %s;
                                                 border-style: solid;
                                                 background-color: %s}
                                      """
                % (self._highlight_str, self._transp_highlight_str)
            )
            if self._actions:
                self._ui.button.setVisible(True)

        else:
            self._ui.box.setStyleSheet("")
            self._ui.button.setVisible(False)

    def set_actions(self, actions):
        """
        Adds a list of QActions to the actions menu for this widget.

        :param actions: List of QActions to add
        """
        self._actions = actions
        for a in self._actions:
            self._menu.addAction(a)

    def resizeEvent(self, event):
        """
        Override the base method.

        Rescale the pixmap when the label resizes.

        :param event: The resize event payload.
        :type event: QResizeEvent
        """

        self.set_scaled_thumbnail()

    def set_scaled_thumbnail(self, pixmap=None):
        """
        Set the thumbnail label pixmap.

        Scale the pixmap to the label's size and center it within the label. Keep the aspect
        ratio of the pixmap when scaling.

        :param pixmap: The pixmap to set on the label.
        :type pixmap: QtGui.QPixmap
        """

        pixmap = pixmap or self._ui.thumbnail.pixmap()
        if not pixmap:
            return

        width = self._ui.thumbnail.width()
        height = self._ui.thumbnail.height()
        scaled_pixmap = pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio)
        self._ui.thumbnail.setPixmap(scaled_pixmap)
