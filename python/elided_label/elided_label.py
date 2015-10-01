# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
A QLabel that elides text and adds ellipses if the text doesn't fit
correctly within the widget frame.  Handles rich-text.
"""

import sgtk
from sgtk.platform.qt import QtCore, QtGui

class ElidedLabel(QtGui.QLabel):
    """
    Label that gracefully handles when the text doesn't fit 
    within the given space. 
    """
    def __init__(self, parent=None):
        """
        :param parent:  The parent QWidget
        :type parent: :class:`~PySide.QtGui.QWidget`        
        """
        QtGui.QLabel.__init__(self, parent)

        self._elide_mode = QtCore.Qt.ElideRight
        self._actual_text = ""

    #@property
    def _get_elide_mode(self):
        """
        Returns current elide mode 

        :returns:   The current elide mode, either QtCore.Qt.ElideLeft or QtCore.Qt.ElideRight 
        """
        return self._elide_mode
    
    def _set_elide_mode(self, value):
        """
        Set the current elide mode.

        :param value:   The elide mode to use - must be either QtCore.Qt.ElideLeft or QtCore.Qt.ElideRight 
        """
        if (value != QtCore.Qt.ElideLeft
            and value != QtCore.Qt.ElideRight):
            raise ValueError("elide_mode must be set to either QtCore.Qt.ElideLeft or QtCore.Qt.ElideRight")
        self._elide_mode = value
        self._update_elided_text()
    
    #: Property to get or set the elide mode. The value provided 
    #: should be either QtCore.Qt.ElideLeft or QtCore.Qt.ElideRight
    elide_mode = property(_get_elide_mode, _set_elide_mode)

    def text(self):
        """
        Overridden base method to return the original unmodified text

        :returns:   The original unmodified text
        """
        return self._actual_text

    def setText(self, text):
        """
        Overridden base method to set the text on the label

        :param text:    The text to set on the label
        """
        self._actual_text = text
        self._update_elided_text()

    def resizeEvent(self, event):
        """
        Overridden base method called when the widget is resized.

        :param event:    The resize event
        """
        self._update_elided_text()

    def _update_elided_text(self):
        """
        Update the elided text on the label
        """
        text = self._elide_text(self._actual_text, self._elide_mode)
        QtGui.QLabel.setText(self, text)

    def _elide_text(self, text, elide_mode):
        """
        Elide the specified text using the specified mode

        :param text:        The text to elide
        :param elide_mode:  The elide mode to use
        :returns:           The elided text.
        """
        # target width is the label width:
        target_width = self.width()

        # Use a QTextDocument to measure html/richtext width 
        doc = QtGui.QTextDocument()
        try:
            doc.setHtml(text)
            doc.setDefaultFont(self.font())

            # if line width is already less than the target width then great!
            line_width = doc.idealWidth()
            if line_width <= target_width:
                return text

            # depending on the elide mode, insert ellipses in the correct place
            cursor = QtGui.QTextCursor(doc)
            ellipses = ""
            if elide_mode != QtCore.Qt.ElideNone:
                # add the ellipses in the correct place:
                if elide_mode == QtCore.Qt.ElideLeft:
                    ellipses = "..."
                    cursor.setPosition(0)
                elif elide_mode == QtCore.Qt.ElideRight:
                    ellipses = "..."
                    char_count = doc.characterCount()
                    cursor.setPosition(char_count-1)
                cursor.insertText(ellipses)
            ellipses_len = len(ellipses)

            # remove characters until the text fits within the target width:
            while line_width > target_width:
                # if string is less than the ellipses length then just return
                # an empty string
                char_count = doc.characterCount()
                if char_count <= ellipses_len:
                    return ""

                # calculate the number of characters to remove - should always remove at least 1
                # to be sure the text gets shorter!
                line_width = doc.idealWidth()
                p = target_width/line_width
                # play it safe and remove a couple less than the calculated amount
                chars_to_delete = max(1, char_count - int(float(char_count) * p)-2)

                # remove the characters:
                if elide_mode == QtCore.Qt.ElideLeft:
                    cursor.setPosition(ellipses_len)
                    cursor.setPosition(chars_to_delete + ellipses_len, QtGui.QTextCursor.KeepAnchor)
                else:
                    # default is to elide right
                    cursor.setPosition(char_count - chars_to_delete - ellipses_len - 1)
                    cursor.setPosition(char_count - ellipses_len - 1, QtGui.QTextCursor.KeepAnchor)
                cursor.removeSelectedText()

                # update line width:
                line_width = doc.idealWidth()

            return doc.toHtml()
        finally:
            # clean up the doc:
            doc.deleteLater()


