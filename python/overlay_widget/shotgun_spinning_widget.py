# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


import math

from tank.platform.qt import QtCore, QtGui

# load resources
from .ui import resources_rc # noqa


class ShotgunSpinningWidget(QtGui.QWidget):
    """
    Overlay widget that can be placed on top over any QT widget.
    Once you have placed the overlay widget, you can use it to
    display information, errors, a spinner etc.
    """

    MODE_OFF = 0
    MODE_SPIN = 1
    MODE_PROGRESS = 2

    def __init__(self, parent):
        """
        :param parent: Widget to attach the overlay to
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        QtGui.QWidget.__init__(self, parent)

        # turn off the widget
        self.setVisible(False)
        self._mode = self.MODE_OFF

        # setup spinner timer
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._on_animation)
        self._spin_angle = 0
        self._spin_angle_to = 0
        self._previous_spin_angle_to = 0
        self._heartbeat = 0

        self._sg_icon = QtGui.QPixmap(":/tk_framework_qtwidgets.overlay_widget/sg_logo.png")

    ############################################################################################
    # public interface
    def start_spin(self):
        """
        Enables the overlay and shows an animated spinner.

        If you want to stop the spinning, call :meth:`hide`.
        """
        self._timer.start(40)
        self.setVisible(True)
        self._mode = self.MODE_SPIN

    def start_progress(self):
        self.setVisible(True)
        self._timer.start(40)
        self._mode = self.MODE_PROGRESS
        self._spin_angle_to = 0
        self._spin_angle = 0

    def report_progress(self, current):
        self._spin_angle = max(self._previous_spin_angle_to, self._spin_angle)
        self._previous_spin_angle_to = self._spin_angle_to
        self._spin_angle_to = 360 * current
        self.repaint()

    def hide(self):
        """
        Hides the overlay.

        :param hide_errors: If set to False, errors are not hidden.
        """
        self._timer.stop()
        self._mode = self.MODE_OFF
        self.setVisible(False)

    ############################################################################################
    # internal methods

    def _on_animation(self):
        """
        Spinner async callback to help animate the progress spinner.
        """
        if self._mode == self.MODE_SPIN:
            self._spin_angle += 1
            if self._spin_angle == 90:
                self._spin_angle = 0
        elif self._mode == self.MODE_PROGRESS:
            # If the current spin angle has not reached the destination yet,
            # increment it, but not past.
            self._spin_angle = min(self._spin_angle_to, self._spin_angle + 1)
            self._heartbeat = (self._heartbeat + 1) % 25

        self.repaint()

    def _draw_opened_circle(self, painter, start_angle, span_angle):
        # show the spinner
        painter.translate((painter.device().width() / 2) - 40,
                          (painter.device().height() / 2) - 40)

        pen = QtGui.QPen(QtGui.QColor("#424141"))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPixmap(QtCore.QPoint(8, 24), self._sg_icon)

        r = QtCore.QRectF(0.0, 0.0, 80.0, 80.0)
        # drawArc accepts 1/16th on angles.
        painter.drawArc(r, start_angle * 16, span_angle * 16)

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
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            # now draw different things depending on mode
            if self._mode == self.MODE_SPIN:

                self._draw_opened_circle(
                    painter,
                    self._spin_angle * 4,
                    340
                )

            elif self._mode == self.MODE_PROGRESS:
                self._draw_opened_circle(
                    painter,
                    # Start at noon
                    90,
                    # Go clockwise
                    -self._spin_angle
                )

                self._draw_heartbeat(painter)

        finally:
            painter.end()

    def _draw_heartbeat(self, painter):

        amplitude = (math.fabs(self._heartbeat - 12.5) / 12.5) * 6

        angle = self._spin_angle - 90
        y = math.sin(math.radians(angle))
        x = math.cos(math.radians(angle))

        pen = QtGui.QPen(QtGui.QColor("#424141"))
        brush = QtGui.QBrush(QtGui.QColor("#424141"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(brush)

        painter.drawEllipse(
            QtCore.QRectF(
                x * 40 + 40 - amplitude / 2,
                y * 40 + 40 - amplitude / 2,
                amplitude,
                amplitude,
            )
        )
