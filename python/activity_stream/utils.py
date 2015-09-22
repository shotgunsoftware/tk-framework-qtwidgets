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
from datetime import datetime , timedelta

def create_round_thumbnail(image):
    """
    Create a circle thumbnail 80px wide, given a thumbnail image
    
    :param image: QImage to process
    :returns: QPixmap object
    """
    CANVAS_SIZE = 80

    # make base image
    base_image = QtGui.QPixmap(CANVAS_SIZE, CANVAS_SIZE)
    base_image.fill(QtCore.Qt.transparent)
    
    # now attempt to load the image
    # pixmap will be a null pixmap if load fails    
    thumb = QtGui.QPixmap.fromImage(image)
    
    if not thumb.isNull():
            
        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = thumb.scaled(CANVAS_SIZE, 
                                    CANVAS_SIZE, 
                                    QtCore.Qt.KeepAspectRatioByExpanding, 
                                    QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)
        painter.drawEllipse(0, 0, CANVAS_SIZE, CANVAS_SIZE)             
        painter.end()
    
    return base_image

def create_square_48_thumbnail(image):
    """
    Given a thumbnail image, create a 48px square image
    
    :param image: QImage with thumbnail
    :returns: QPixmap object
    """
    return __create_rounded_rect_thumbnail(image, 48, 48, 4)
    
def create_rectangular_256x144_thumbnail(image):
    """
    Given a thumbnail image, create a 256x144px image
    
    :param image: QImage with thumbnail
    :returns: QPixmap object
    """
    return __create_rounded_rect_thumbnail(image, 256, 144, 5)

def __create_rounded_rect_thumbnail(image, canvas_width, canvas_height, radius):
    """
    Given a qimage shotgun thumbnail, create a publish icon
    with the thumbnail composited onto a centered otherwise empty canvas.
    The thumbnail will be taking up all the space in the image.
    
    :param image: QImage to load thumbnail from
    :param canvas_width: Width of image to generate, in pixels
    :param canvas_height: Heiht of image to generate, in pixels
    :param radius: Corner radius of image to generate, in pixels
    :returns: QPixmap object
    """
    # get the base image
    base_image = QtGui.QPixmap(canvas_width, canvas_height)
    base_image.fill(QtCore.Qt.transparent)
    
    # now attempt to load the image
    # pixmap will be a null pixmap if load fails    
    thumb = QtGui.QPixmap.fromImage(image)
    
    if not thumb.isNull():
            
        # scale it down to fit inside a frame
        thumb_scaled = thumb.scaled(canvas_width, 
                                    canvas_height, 
                                    QtCore.Qt.KeepAspectRatioByExpanding, 
                                    QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)
        painter.setPen(QtGui.QPen())
        
        painter.drawRoundedRect(0,  
                                0, 
                                canvas_width, 
                                canvas_height, 
                                radius, 
                                radius)
        
        painter.end()
    
    return base_image
    

