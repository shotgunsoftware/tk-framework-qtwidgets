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


class ShotgunOverlayWidget(QtGui.QWidget):
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

    def __init__(self, parent):
        """
        :param parent: Widget to attach the overlay to
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        QtGui.QWidget.__init__(self, parent)

        # hook up a listener to the parent window so we
        # can resize the overlay at the same time as the parent window
        # is being resized.
        filter = ResizeEventFilter(parent)
        filter.resized.connect(self._on_parent_resized)
        parent.installEventFilter(filter)

        self._shotgun_spinning_widget = ShotgunSpinningWidget(self)

        # make it transparent
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # turn off the widget
        self.setVisible(False)
        self._mode = self.MODE_OFF

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
        self._shotgun_spinning_widget.start_spin()
        self._mode = self.MODE_SPIN
        self.setVisible(True)

    def show_error_message(self, msg):
        """
        Enables the overlay and displays an
        a error message centered in the middle of the overlay.

        :param msg: Message to display
        """
        self._shotgun_spinning_widget.hide()
        self.setVisible(True)
        self._message = msg
        self._mode = self.MODE_ERROR
        self.repaint()

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
            self._shotgun_spinning_widget.hide()
            self.setVisible(True)
            self._message = msg
            self._mode = self.MODE_INFO_TEXT
            self.repaint()
            return True

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
            self._shotgun_spinning_widget.hide()
            self.setVisible(True)
            self._message_pixmap = pixmap
            self._mode = self.MODE_INFO_PIXMAP
            self.repaint()
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

    def paintEvent(self, event):
        """
        Render the UI.
        """
        if self._mode == self.MODE_OFF:
            return

        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            # set up semi transparent backdrop
            overlay_color = QtGui.QColor("#1B1B1B")
            painter.setBrush(QtGui.QBrush(overlay_color))
            painter.setPen(QtGui.QPen(overlay_color))
            painter.drawRect(0, 0, painter.device().width(), painter.device().height())

            if self._mode == self.MODE_INFO_TEXT:
                # show text in the middle
                pen = QtGui.QPen(QtGui.QColor("#888888"))
                painter.setPen(pen)
                text_rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
                text_flags = QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.TextWordWrap
                painter.drawText(text_rect, text_flags, self._message)

            elif self._mode == self.MODE_ERROR:
                # show error text in the center
                pen = QtGui.QPen(QtGui.QColor("#C8534A"))
                painter.setPen(pen)
                text_rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
                text_flags = QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.TextWordWrap
                painter.drawText(text_rect, text_flags, self._message)

            elif self._mode == self.MODE_INFO_PIXMAP:
                # draw image
                painter.translate((painter.device().width() / 2) - (self._message_pixmap.width() / 2),
                                  (painter.device().height() / 2) - (self._message_pixmap.height() / 2))

                painter.drawPixmap(QtCore.QPoint(0, 0), self._message_pixmap)

        finally:
            painter.end()

        return super(ShotgunOverlayWidget, self).paintEvent(event)


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
