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

import time
import math

class SpinnerWidget(QtGui.QWidget):
    """
    A simple widget that draws an animated spinner that spins whilst visible.
    """
    def __init__(self, parent=None):
        """
        :param parent:    The parent widget
        :type parent:     :class:`~PySide.QtGui.QWidget`
        """
        QtGui.QWidget.__init__(self, parent)

        # public properties:
        self.fps = 20
        self.border = 2
        self.line_width = 2
        self.arc_length = 300
        self.seconds_per_spin = 3

        # timer used to force a repaint:
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._on_timer_timeout)

        # keep track of the current start angle to avoid 
        # unnecessary repaints
        self._start_angle = 0

    def paintEvent(self, event):
        """
        Paint the widget

        :param event:    The QPaintEvent event
        """
        # call the base paint event:
        QtGui.QWidget.paintEvent(self, event)

        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            # use the foreground colour to paint with:
            fg_col = self.palette().color(self.foregroundRole())
            pen = QtGui.QPen(fg_col)
            pen.setWidth(self.line_width)
            painter.setPen(pen)

            border = self.border + int(math.ceil(self.line_width / 2.0))
            r = QtCore.QRect(0, 0, self.width(), self.height())
            r.adjust(border, border, -border, -border)

            # draw the arc:    
            painter.drawArc(r, -self._start_angle * 16, self.arc_length * 16)
            r = None

        finally:
            painter.end()
            painter = None

    def showEvent(self, event):
        """
        Called when the widget is being shown - ensures the timer is running
        so that the animation plays

        :param event:    The event
        """
        if not self._timer.isActive():
            self._timer.start(1000 / max(1, self.fps))
        QtGui.QWidget.showEvent(self, event)

    def hideEvent(self, event):
        """
        Called when the widget is being hidden - ensures the timer is stopped
        to avoid unnecessary painting

        :param even:    The event
        """
        self._timer.stop()
        QtGui.QWidget.hideEvent(self, event)

    def closeEvent(self, event):
        """
        Called when the widget is being closed - ensures the timer is stopped
        to avoid unnecessary painting

        :param even:    The event
        """
        self._timer.stop()
        QtGui.QWidget.closeEvent(self, event)

    def _on_timer_timeout(self):
        """
        Slot triggered when the timer times out and used to trigger a repaint of
        the widget.
        """
        if not self.isVisible():
            # nothing to do!
            return

        # calculate the spin angle as a function of the current time so that all 
        # spinners appear in sync!
        t = time.time()
        whole_seconds = int(t)
        p = (whole_seconds % self.seconds_per_spin) + (t - whole_seconds)
        angle = int((360 * p)/self.seconds_per_spin)

        if angle == self._start_angle:
            # angle hasn't changed!
            return

        self._start_angle = angle

        # trigger a repaint for the widget:
        self.update()



