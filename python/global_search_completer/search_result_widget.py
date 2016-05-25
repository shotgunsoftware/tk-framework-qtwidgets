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
 
# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from .ui.search_result_widget import Ui_SearchResultWidget

class SearchResultWidget(QtGui.QWidget):
    """
    Widget that represents a single search match that shows up in the
    auto completer global search matches popup.
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        QtGui.QWidget.__init__(self, parent)

        # make sure this widget isn't shown
        self.setVisible(False)
        
        # set up the UI
        self.ui = Ui_SearchResultWidget() 
        self.ui.setupUi(self)
        
        # the property stylesheet syntax seems brittle and hacky so 
        # keeping the style sheet modifications local here rather
        # than in global css        
        self._css_selected = """
            #box { border-width: 2px; 
                   border-radius: 4px;
                   border-color: rgb(48, 167, 227);
                   background-color: rgba(48, 167, 227, 15%);
                   border-style: solid;
            }
            """        
        self._css_not_selected = """
            #box { border-width: 2px; 
                   border-radius: 4px;
                   border-color: rgba(0, 0, 0, 0%);
                   border-style: solid;
            }
            """    
        
        self.set_selected(False)    

                                    
    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not
        
        :param selected: True if selected, false if not
        """
        if selected:
            self.ui.box.setStyleSheet(self._css_selected)
        else:
            self.ui.box.setStyleSheet(self._css_not_selected)
            
    
    def set_thumbnail(self, pixmap):
        """
        Set a thumbnail given the current pixmap.
        The pixmap must be 100x100 or it will appear squeezed
        
        :param pixmap: pixmap object to use
        """
        if pixmap is None:
            self.ui.thumbnail.setVisible(False)
        else:
            self.ui.thumbnail.setVisible(True)
            self.ui.thumbnail.setPixmap(self.create_rectangular_thumbnail(pixmap))
            
            
    def create_rectangular_thumbnail(self, thumb):
        """
        Scale a given pixmap down to a given resolution
        
        :param thumb: pixmap to scale
        :returns: scaled thumbnail
        """
        
        #TODO: this would be great to add to the qtwidgets framework
    
        CANVAS_WIDTH = 48
        CANVAS_HEIGHT = 38
    
        # get the 512 base image
        base_image = QtGui.QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
        base_image.fill(QtCore.Qt.transparent)
                
        if not thumb.isNull():
                
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
    
            
    def set_text(self, label):
        """
        Populate the lines of text in the widget
        
        :param header: Header text as string
        :param body: Body text as string
        """
        self.ui.label.setText(label)

    @staticmethod
    def calculate_size():
        """
        Calculates and returns a suitable size for this widget.
        
        :returns: Size of the widget
        """        
        return QtCore.QSize(300, 46)


