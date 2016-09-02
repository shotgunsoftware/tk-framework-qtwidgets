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
        self._text_fade = _TextFadeOverlay(parent=self)

    def set_selected(self, selected):
        """
        Adjust the style sheet to indicate selection or not
        
        :param selected: True if selected, false if not
        """
        if selected:
            self.ui.box.setStyleSheet(self._css_selected)
        else:
            self.ui.box.setStyleSheet(self._css_not_selected)

        self.show_fade(not selected)

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
            self.ui.thumbnail.setPixmap(pixmap)
            
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

    def resizeEvent(self, event):
        """
        Handles updating the geometry for the text fade overlay.

        Overrides the same method from ``QtGui.QWidget``
        """

        self._text_fade.setGeometry(self.rect())
        super(SearchResultWidget, self).resizeEvent(event)

    def show_fade(self, show):
        """
        Show or hide the text fade at the bottom of the results.

        :param bool show: Show or hide the text fade widget.
        :return:
        """

        if not hasattr(self, "_text_fade"):
            return

        if show:
            self._text_fade.show()
        else:
            self._text_fade.hide()


class _TextFadeOverlay(QtGui.QWidget):
    """
    A sharp gradient to prevent harsh text chopping in result widget.
    """

    def paintEvent(self, event):
        """
        Handles painting the text fade overlay.

        Overrides the same method from ``QtGui.QWidget``
        """
        painter = QtGui.QPainter(self)

        # calculate the rectangle to paint the overlay.
        # it should only be
        gradient_rect = QtCore.QRect(
            60,                          # stay to the right of the thumbnail
            event.rect().bottom() - 8,   # only 8 pixels high from the bottom
            event.rect().right() + 1,    # ensure covers full width
            event.rect().bottom()
        )

        # vertical gradient
        gradient = QtGui.QLinearGradient(
            gradient_rect.topLeft(),
            gradient_rect.bottomLeft()
        )

        # transparent -> base color, in first 15% of height of rect
        gradient.setColorAt(0, QtGui.QColor(0, 0, 0, 0))
        gradient.setColorAt(.15, self.palette().base().color())

        # paint it
        painter.fillRect(gradient_rect, gradient)
        painter.end()


