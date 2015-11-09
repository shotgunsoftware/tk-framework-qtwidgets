# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sys
import tank

from tank.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog

def show_help_screen(parent, bundle, pixmaps):
    """
    Show help screen window.
    
    :param parent: Parent window. The help screen will be centered on top of this window.
    :type parent: :class:`PySide.QtGui.QWidget`
    
    :param bundle: Bundle object to associate with
    :type bundle: :class:`sgtk.platform.Application`, 
                  :class:`sgtk.platform.Engine` or 
                  :class:`sgtk.platform.Framework`
    
    :param pixmaps: List of images, all 650x400 px
    :type pixmaps: List of :class:`PySide.QtGui.QPixmap`  
    """
    gui = Dialog(parent, bundle, pixmaps)
    gui.setWindowTitle("Toolkit Help")
    gui.show()
    # attach the object to the main parent object - this is
    # to help older versions of PySide which get confused
    # when a PySide object handle is lost but the 
    # underlying QT object persists.
    parent.__help_screen = gui
    # center on top of parent window
    gui.move(gui.parent().window().frameGeometry().center() - gui.window().rect().center())
    gui.repaint()

class Dialog(QtGui.QDialog):
    """
    Help screen dialog.
    """
    
    # direction when turning a page
    NEXT_PAGE, PREVIOUS_PAGE = range(2)
    
    def __init__(self, parent, bundle, pixmaps):
        """
        Constructor.
        
        :param parent: Parent window. The help screen will be centered on top of this window.
        :param bundle: Bundle object to associate with (app, engine, framework)
        :param pixmaps: List of QPixmap objects, all 650x400 px        
        """
        
        # it seems some versions of linux are having issues with the splash screen mode,
        # so disable this
        if "linux" in sys.platform:
            QtGui.QDialog.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint)
        else: 
            QtGui.QDialog.__init__(self, parent, QtCore.Qt.SplashScreen | QtCore.Qt.WindowStaysOnTopHint)
        
        self._bundle = bundle

        self.__page_anim_grp = None

        # set up the UI
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)
        
        if self._bundle.documentation_url is None:
            self.ui.view_documentation.setEnabled(False)
        
        self.ui.view_documentation.clicked.connect(self._on_doc)
        self.ui.close.clicked.connect(self.close)
        
        self.ui.left_arrow.clicked.connect(self._on_left_arrow_click)
        self.ui.right_arrow.clicked.connect(self._on_right_arrow_click)
        
        # we start at index zero so disable the left arrow
        self.ui.left_arrow.setVisible(False)
        if len(pixmaps) == 1:
            # only one image. So disable the right arrow aswell
            self.ui.right_arrow.setVisible(False)
        
        # make GC happy
        self._widgets = []
        self._pages = []
        
        for p in pixmaps:
            
            if p.width() != 650 or p.height() != 400:
                raise tank.TankError("Image not found or image resolution not 650x400px!")
            
            page = QtGui.QWidget()
            self._pages.append(page)
            layout = QtGui.QVBoxLayout(page)
            layout.setContentsMargins(2, 2, 2, 2)
            label = QtGui.QLabel(page)
            label.setMinimumSize(QtCore.QSize(650, 400))
            label.setMaximumSize(QtCore.QSize(650, 400))
            label.setPixmap(p)
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)
            self.ui.stackedWidget.addWidget(page)
            self._widgets.extend([p, page, layout, label])
        
        # set first page
        self.ui.stackedWidget.setCurrentIndex(0)
        self._num_images = len(pixmaps)
        
    def _on_left_arrow_click(self):
        """
        User clicks the left arrow
        """
        self.__turn_page(Dialog.PREVIOUS_PAGE)
        
    def _on_right_arrow_click(self):
        """
        User clicks the right arrow
        """
        self.__turn_page(Dialog.NEXT_PAGE)

    def __turn_page(self, direction=NEXT_PAGE):
        """
        Turn the page in the direction specified
        
        :param direction:    The direction to turn the page
        """
        current_index = self.ui.stackedWidget.currentIndex()
        dst_index = current_index
        page_offset = 650
        
        # depending on the direction, figure out the destination page 
        # and page offset for animation:
        if direction == Dialog.NEXT_PAGE:
            dst_index += 1
            page_offset = 650
            
            # update the arrow visibility so that the right arrow is
            # hidden if we're on the last page:
            self.ui.right_arrow.setVisible(dst_index < (self._num_images - 1))
            self.ui.left_arrow.setVisible(True)
        else:
            # going back a page
            dst_index -= 1
            page_offset = -650
            
            # update the arrow visibility so that the left arrow is
            # hidden if we're on the first page:
            self.ui.right_arrow.setVisible(True)
            self.ui.left_arrow.setVisible(dst_index > 0)
        
        if not hasattr(QtCore, "QAbstractAnimation"):
            # this version of Qt (probably PyQt4) doesn't contain
            # Q*Animation classes so just change the page:
            self.ui.stackedWidget.setCurrentIndex(dst_index)
        else:
            anim_duration = 600# milliseconds
            
            if self.__page_anim_grp and self.__page_anim_grp.state() == QtCore.QAbstractAnimation.Running:
                # the previous animation hasn't finished yet so jump to the end!
                self.__page_anim_grp.setCurrentTime(anim_duration)
            
            # animate the transition from one page to the next:
            current_page = self._pages[current_index]
            dst_page = self._pages[dst_index]

            # reset positions
            dst_page.move(dst_page.x()+page_offset, dst_page.y())
            self.ui.stackedWidget.setCurrentIndex(dst_index)
            # still need to show the current page whilst it transitions
            current_page.show()
            current_page.raise_()       
            
            # animate the current page away
            self.__anim = QtCore.QPropertyAnimation(current_page, "pos")
            self.__anim.setDuration(anim_duration)
            self.__anim.setStartValue(QtCore.QPoint(current_page.x(), current_page.y()))
            self.__anim.setEndValue(QtCore.QPoint(current_page.x()-page_offset, current_page.y()))
            self.__anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
    
            # animate the new page in:
            self.__anim2 = QtCore.QPropertyAnimation(dst_page, "pos")
            self.__anim2.setDuration(anim_duration)
            self.__anim2.setStartValue(QtCore.QPoint(dst_page.x()+page_offset, dst_page.y()))
            self.__anim2.setEndValue(QtCore.QPoint(dst_page.x(), dst_page.y()))
            self.__anim2.setEasingCurve(QtCore.QEasingCurve.OutCubic)
    
            # create a parallel animation group so that both pages animate at
            # the same time:
            self.__page_anim_grp = QtCore.QParallelAnimationGroup()
            self.__page_anim_grp.addAnimation(self.__anim)
            self.__page_anim_grp.addAnimation(self.__anim2)
            
            # run the animation/transition
            self.__page_anim_grp.start()
        
    def _on_doc(self):
        """
        Launch doc url.
        """
        self._bundle.log_debug("Opening documentation url %s..." % self._bundle.documentation_url)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(self._bundle.documentation_url))
        
        
        
        
        
