# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import tempfile

from sgtk.platform.qt import QtCore, QtGui


class ScreenGrabber(QtGui.QDialog):
    """
    A transparent tool dialog for selecting an area (QRect) on the screen.

    This tool does not by itself perform a screen capture. The resulting
    capture rect can be used (e.g. with the get_desktop_pixmap function) to
    blit the selected portion of the screen into a pixmap.
    """

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(ScreenGrabber, self).__init__(parent)

        self._opacity = 1
        self._click_pos = None
        self._capture_rect = QtCore.QRect()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.CustomizeWindowHint |
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)

        desktop = QtGui.QApplication.instance().desktop()
        desktop.resized.connect(self._fit_screen_geometry)
        desktop.screenCountChanged.connect(self._fit_screen_geometry)

    @property
    def capture_rect(self):
        """
        The resulting QRect from a previous capture operation.
        """
        return self._capture_rect

    def paintEvent(self, evt):
        """
        Paint event
        """
        # Convert click and current mouse positions to local space.
        mouse_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        click_pos = None
        if self._click_pos is not None:
            click_pos = self.mapFromGlobal(self._click_pos)

        painter = QtGui.QPainter(self)

        # Draw background. Aside from aesthetics, this makes the full
        # tool region accept mouse events.
        painter.setBrush(QtGui.QColor(0, 0, 0, self._opacity))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(evt.rect())

        # Clear the capture area
        if click_pos is not None:
            capture_rect = QtCore.QRect(click_pos, mouse_pos)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.drawRect(capture_rect)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 64), 1, QtCore.Qt.DotLine)
        painter.setPen(pen)

        # Draw cropping markers at click position
        if click_pos is not None:
            painter.drawLine(evt.rect().left(), click_pos.y(),
                             evt.rect().right(), click_pos.y())
            painter.drawLine(click_pos.x(), evt.rect().top(),
                             click_pos.x(), evt.rect().bottom())

        # Draw cropping markers at current mouse position
        painter.drawLine(evt.rect().left(), mouse_pos.y(),
                         evt.rect().right(), mouse_pos.y())
        painter.drawLine(mouse_pos.x(), evt.rect().top(),
                         mouse_pos.x(), evt.rect().bottom())

    def keyPressEvent(self, evt):
        """
        Key press event
        """
        # for some reason I am not totally sure about, it looks like
        # pressing escape while this dialog is active crashes Maya.
        # I tried subclassing closeEvent, but it looks like the crashing
        # is triggered before the code reaches this point.
        # by sealing the keypress event and not allowing any further processing
        # of the escape key (or any other key for that matter), the 
        # behaviour can be successfully avoided.
        pass
    
    def mousePressEvent(self, evt):
        """
        Mouse click event
        """
        if evt.button() == QtCore.Qt.LeftButton:
            # Begin click drag operation
            self._click_pos = evt.globalPos()

    def mouseReleaseEvent(self, evt):
        """ 
        Mouse release event
        """
        if evt.button() == QtCore.Qt.LeftButton and self._click_pos is not None:
            # End click drag operation and commit the current capture rect
            self._capture_rect = QtCore.QRect(self._click_pos,
                                              evt.globalPos()).normalized()
            self._click_pos = None
        self.close()

    def mouseMoveEvent(self, evt):
        """
        Mouse move event
        """
        self.repaint()

    def showEvent(self, evt):
        """
        Show event
        """
        self._fit_screen_geometry()
        # Start fade in animation
        fade_anim = QtCore.QPropertyAnimation(self, "_opacity_anim_prop", self)
        fade_anim.setStartValue(self._opacity)
        fade_anim.setEndValue(127)
        fade_anim.setDuration(300)
        fade_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        fade_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _set_opacity(self, value):
        """
        Animation callback for opacity
        """
        self._opacity = value
        self.repaint()

    def _get_opacity(self):
        """
        Animation callback for opacity
        """
        return self._opacity

    _opacity_anim_prop = QtCore.Property(int, _get_opacity, _set_opacity)

    def _fit_screen_geometry(self):
        # Compute the union of all screen geometries, and resize to fit.
        desktop = QtGui.QApplication.instance().desktop()
        workspace_rect = QtCore.QRect()
        for i in range(desktop.screenCount()):
            workspace_rect = workspace_rect.united(desktop.screenGeometry(i))
        self.setGeometry(workspace_rect)


def get_desktop_pixmap(rect):
    """
    Performs a screen capture on the specified QRect, returning a QPixmap.
    """
    desktop = QtGui.QApplication.instance().desktop()
    return QtGui.QPixmap.grabWindow(desktop.winId(), rect.x(), rect.y(),
                                    rect.width(), rect.height())

def screen_capture():
    """
    Modally display the screen capture tool, returning a QPixmap.
    """
    tool = ScreenGrabber()
    tool.exec_()
    return get_desktop_pixmap(tool.capture_rect)


def screen_capture_file(output_path=None):
    """
    Modally display the screen capture tool, saving to a file.
    
    :param output_path: Path to save to. If no path is specified,
    a temp path is generated.
    :returns: path where screenshot was saved.
    """
    if output_path is None:
        output_path = tempfile.NamedTemporaryFile(suffix=".png",
                                                  prefix="screencapture_",
                                                  delete=False).name
    pixmap = screen_capture()
    pixmap.save(output_path)
    return output_path


