# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from tank.platform.qt import QtCore, QtGui

# load resources
from .ui import resources_rc # noqa
from .shotgun_spinning_widget import ShotgunSpinningWidget


class ShotgunOverlayWidget(QtGui.QLabel):
    """
    Overlay widget that can be placed on top over any QT widget.
    Once you have placed the overlay widget, you can use it to
    display information, errors, a spinner etc.
    """

    MODE_OFF = 0
    MODE_SPIN = 1
    MODE_ERROR = 2
    MODE_INFO_TEXT = 3
    MODE_INFO_PIXMAP = 4
    MODE_PROGRESS = 5

    ERROR_COLOR = "#C8534A;"
    INFO_COLOR = "#888888;"

    def __init__(self, parent):
        """
        :param parent: Widget to attach the overlay to
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        QtGui.QLabel.__init__(self, parent)

        # hook up a listener to the parent window so we
        # can resize the overlay at the same time as the parent window
        # is being resized.
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)

        self._shotgun_spinning_widget = ShotgunSpinningWidget(self)

        # make it transparent
        self.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.TextWordWrap)

        self.setOpenExternalLinks(True)
        self.setWordWrap(True)
        self.setStyleSheet("background-color: #1B1B1B")

        # turn off the widget
        self.hide()

        self._message_pixmap = None
        self._message = None
        self._sg_icon = QtGui.QPixmap(":/tk_framework_qtwidgets.overlay_widget/sg_logo.png")

    ############################################################################################
    # public interface
    def start_spin(self):
        """
        Enables the overlay and shows an animated spinner.

        If you want to stop the spinning, call :meth:`hide`.
        """
        self._set_mode(self.MODE_SPIN)

    def show_error_message(self, msg):
        """
        Enables the overlay and displays an
        a error message centered in the middle of the overlay.

        :param msg: Message to display
        """
        self._set_mode(self.MODE_ERROR, msg)

    def show_message(self, msg):
        """
        Display a message centered on the overlay.
        If an error is already being displayed by the overlay at this point,
        nothing will happen.

        :param msg: Message to display
        :returns: True if message was displayed, False otherwise
        """
        if self._mode == self.MODE_ERROR:
            return False
        else:
            self._set_mode(self.MODE_INFO_TEXT, msg)
            return True

    def _set_mode(self, mode, payload=None):
        """
        Handles the state of the widget. It will set or reset text/pixmap/spinner
        depending on the state we're moving to.

        :param mode: Mode we're switching to.
        :param payload: Can be a string or a QtGui.QPixmap, that needs to be set
            on the widget.
        """

        # Decide if we need to show the spinning cursor or not.
        if mode == self.MODE_SPIN:
            self._shotgun_spinning_widget.start_spin()
        else:
            self._shotgun_spinning_widget.hide()

        # Decide if we need to show the pixmap or not.
        if mode == self.MODE_INFO_PIXMAP:
            self.setPixmap(payload)
        else:
            self.setPixmap(None)

        # Decide which kind of string we need to show.
        if mode == self.MODE_ERROR:
            self.setText(
                "<font style='color: %s'>%s</font>" %
                (self.ERROR_COLOR, payload.replace("\n", "<br>"))
            )
        elif mode == self.MODE_INFO_TEXT:
            self.setText(
                "<font style='color: #%s;'>%s</font>" %
                (self.NORMAL_COLOR, payload.replace("\n", "<br>"))
            )
        else:
            self.setText("")

        # User is trying to display something, so make the overlay visible.
        self.setVisible(True)

        self._mode = mode

    def show_message_pixmap(self, pixmap):
        """
        Show an info message in the form of a pixmap.
        If an error is already being displayed by the overlay,
        the pixmap will not be shown.

        :param pixamp: Image to display
        :type pixmap: :class:`PySide.QtGui.QPixmap`
        :returns: True if pixmap was displayed, False otherwise
        """
        if self._mode == self.MODE_ERROR:
            return False
        else:
            self._set_mode(self.MODE_INFO_PIXMAP, pixmap)
            return True

    def hide(self, hide_errors=True):
        """
        Hides the overlay.

        :param hide_errors: If set to False, errors are not hidden.
        """
        if hide_errors is False and self._mode == self.MODE_ERROR:
            # an error is displayed - leave it up.
            return
        self._shotgun_spinning_widget.hide()
        self._mode = self.MODE_OFF
        self.setVisible(False)

    ############################################################################################
    # internal methods

    def _on_parent_resized(self):
        """
        Special slot hooked up to the event filter.
        When associated widget is resized this slot is being called.
        """
        # resize overlay
        self.resize(self.parentWidget().size())
        self._shotgun_spinning_widget.resize(self.parentWidget().size())


class ResizeEventFilter(QtCore.QObject):
    """
    Event filter which emits a resized signal whenever
    the monitored widget resizes. This is so that the overlay wrapper
    class can be informed whenever the Widget gets a resize event.
    """
    resized = QtCore.Signal()

    def eventFilter(self, obj, event):
        # peek at the message
        if event.type() == QtCore.QEvent.Resize:
            # re-broadcast any resize events
            self.resized.emit()
        # pass it on!
        return False
