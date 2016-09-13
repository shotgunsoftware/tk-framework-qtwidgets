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
from sgtk.platform.qt import QtGui, QtCore

from .ui import resources_rc


def create_rectangular_thumbnail(thumb):
    """
    Scale a given pixmap down to a given resolution

    :param thumb: pixmap to scale
    :returns: scaled thumbnail
    """
    #TODO: this would be great to add to the qtwidgets framework

    CANVAS_WIDTH = 48
    CANVAS_HEIGHT = 38


    if thumb.isNull():
        # to be safe, if thumb is null, use the empty/default thumbnail
        thumb = QtGui.QPixmap(
            ":/tk_framework_qtwidgets.global_search_widget/no_thumbnail.png")


    # get the 512 base image
    base_image = QtGui.QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
    base_image.fill(QtCore.Qt.transparent)

    # scale it down to fit inside a frame of maximum 512x400
    thumb_scaled = thumb.scaled(CANVAS_WIDTH,
                                CANVAS_HEIGHT,
                                QtCore.Qt.KeepAspectRatioByExpanding,
                                QtCore.Qt.SmoothTransformation)

    # now composite the thumbnail on top of the base image
    # bottom align it to make it look nice
    thumb_img = thumb_scaled.toImage()
    brush = QtGui.QBrush(thumb_img)

    painter = QtGui.QPainter(base_image)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setBrush(brush)

    # figure out the offset height wise in order to center the thumb
    height_difference = CANVAS_HEIGHT - thumb_scaled.height()
    width_difference = CANVAS_WIDTH - thumb_scaled.width()

    # center it with wise
    inlay_offset_w = width_difference/2
    # bottom height wise
    #inlay_offset_h = height_difference+CORNER_RADIUS
    inlay_offset_h = height_difference/2

    # note how we have to compensate for the corner radius
    painter.translate(inlay_offset_w, inlay_offset_h)
    painter.drawRect(0, 0, thumb_scaled.width(), thumb_scaled.height())

    painter.end()

    return base_image


class CompleterPixmaps(object):
    """
    A simple class that provides pixmaps for the completer items.

    Usage::

        completer_pixmaps = CompleterPixmaps()
        ...
        item.setIcon(completer_pixmaps.loading)


    Pixmaps provided::

        loading - For use when a completer item is loading
        keyboard - For use when more text is required for the completer
        no_matches - For use when there are no completion matches
        no_thumbnail - For use when there is no thumbnail for a completed item

    """

    # ---- define some pixmaps to reuse while loading/typing/etc

    def __init__(self):

        # loading a pixmap
        self.loading = create_rectangular_thumbnail(
            QtGui.QPixmap(
                ":/tk_framework_qtwidgets.global_search_widget/loading.png"
            )
        )

        # more typing required
        self.keyboard = create_rectangular_thumbnail(
            QtGui.QPixmap(
                ":/tk_framework_qtwidgets.global_search_widget/keyboard.png"
            )
        )

        # no matches found
        self.no_matches = create_rectangular_thumbnail(
            QtGui.QPixmap(
                ":/tk_framework_qtwidgets.global_search_widget/no_match.png"
            )
        )

        # no thumbnail for the entity
        self.no_thumbnail = create_rectangular_thumbnail(
            QtGui.QPixmap(
                ":/tk_framework_qtwidgets.global_search_widget/no_thumbnail.png"
            )
        )
