# Copyright (c) 2016 Shotgun Software Inc.
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


class BubbleWidget(QtGui.QFrame):
    """
    This class represents a drawable "bubble" to display in a :class:`.BubbleEditWidget`

    This widget will stores data for the object it represents. The data can be set
    and accessed via the respective ``get_data()`` and ``set_data()`` methods.

    The widget can display an optional image along with its text. See the display
    related methods ``set_text()`` and ``set_image()`` below.

    :signal: ``remove_clicked()`` - emitted when the widget's ``x`` button clicked.
    """

    # signal emitted when the widget's remove button was clicked
    remove_clicked = QtCore.Signal()

    def __init__(self, parent=None):
        """Initialize the widget.

        :param parent: This widget's parent widget
        :type parent: :class:`~PySide.QtGui.QWidget`
        """
        super(BubbleWidget, self).__init__(parent)

        # placeholder for the underlying data this widget represents in the editor
        self._data = None

        # should not grow or shrink
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # style the look of the bubble
        self.setObjectName("bubble")
        self.setStyleSheet(
            """
            #bubble {
                border: 1px solid black;
                border-radius: 5px;
                background-color: %s;
            }
            """ % self.palette().color(QtGui.QPalette.Button).name()
        )

        # create a remove button for the widget.
        # extract a close button icon from the style and use it
        self.remove_button = QtGui.QPushButton(self)
        style = self.remove_button.style()
        icon = style.standardIcon(style.SP_TitleBarCloseButton)
        self.remove_button.setIcon(icon)
        self.remove_button.setFlat(True)
        self.remove_button.setStyleSheet("border: none")

        # placeholder for the bubble's image
        self.image_label = QtGui.QLabel(self)

        # color the text to use the SG highlight color
        text_color = QtGui.QColor(
            sgtk.platform.current_bundle().style_constants["SG_HIGHLIGHT_COLOR"]
        )
        self.text_label = QtGui.QLabel(self)
        palette = self.text_label.palette()
        palette.setColor(QtGui.QPalette.WindowText, text_color)
        self.text_label.setPalette(palette)

        # layout the widgets
        self.layout = QtGui.QHBoxLayout()
        self.layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.layout.setContentsMargins(3, 1, 3, 1)
        self.layout.setSpacing(2)

        self.layout.addWidget(self.image_label, QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.text_label, QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.remove_button, QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout)

        # emit the "remove_clicked" signal when the button is clicked.
        self.remove_button.clicked.connect(
            lambda: self.remove_clicked.emit()
        )

    def set_text(self, label_text):
        """
        Set the bubble's display text.

        :param str label_text: The display text
        """
        self.text_label.setText(label_text)

    def set_image(self, url):
        """
        Set the bubble's display image.

        :param str url:  The image url to display in the bubble.
        """
        self.image_label.setText("<img src='%s'/>" % url)

    def set_removable(self, removable):
        """
        Set whether or not the bubble is removable.

        Shows or hides the ``x`` button depending on the value of the
        ``removable`` argument.
        :param bool removable: ``True`` if the bubble is removable, ``False`` otherwise.
        """
        if removable:
            self.remove_button.show()
        else:
            self.remove_button.hide()

    def get_data(self):
        """
        Returns the underlying data object this widget represents.

        The return type is intentionally unspecified since, in theory, the
        bubble could represent any type of data.
        """
        return self._data

    def set_data(self, data):
        """
        Set the underlying data object that this widget represents.

        The type of ``data`` is intentionally unspecified since, in theory, the
        bubble could represent any type of data.
        """
        self._data = data


class BubbleEditWidget(QtGui.QTextEdit):
    """
    This is a base class for "bubble" entry widgets.

    Each object is represented by a "bubble" similar to email address entry
    widgets in modern email clients. Subclasses will typically handle the user
    interaction and decide when a new "bubble" should be added to the widget.
    """

    # used as a placeholder for a bubble in the editor
    _OBJECT_REPLACEMENT_CHAR = unichr(0xfffc)

    def __init__(self, parent=None):
        """
        Initialize the widget.

        :param parent: This widget's parent widget
        :type parent: :class:`~PySide.QtGui.QWidget`
        """

        super(BubbleEditWidget, self).__init__(parent)

        self._char_formats = {}

        self._bubble_text_object = _BubbleTextObject(self)
        self.document().documentLayout().registerHandler(
            _BubbleTextObject.OBJECT_TYPE, self._bubble_text_object,
        )

        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)
        self.setMinimumWidth(180)

    def add_bubble(self, bubble):
        """
        Add the supplied :class:`.BubbleWidget` instance to the editor.

        :param bubble: The bubble widget instance.
        :return: A unique id for the added bubble
        :rtype: :obj:`int`
        """

        bubble_id = self._bubble_text_object.add_bubble(bubble)

        # create a character format for the bubble
        char_format = QtGui.QTextCharFormat()
        char_format.setObjectType(self._bubble_text_object.OBJECT_TYPE)
        char_format.setProperty(self._bubble_text_object.BUBBLE_DATA_PROPERTY, bubble_id)

        # keep a reference to the char format so that we can map a cursor to this
        # bubble later on
        self._char_formats[bubble_id] = char_format

        bubble.remove_clicked.connect(
            lambda: self.remove_bubble(bubble_id)
        )

        # insert the bubble character into the text editor and char format it properly
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.insertText(self._OBJECT_REPLACEMENT_CHAR, char_format)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

        return bubble_id

    def clear(self):
        """
        Clears all bubbles from the editor.
        """
        for char_format in self._char_formats.values():
            del char_format
        self._bubble_text_object.clear()
        super(BubbleEditWidget, self).clear()

    def clear_typed_text(self):
        """
        Clears only typed text (not bubbles) from the editor.
        """

        text = self.toPlainText()
        cursor = self.textCursor()

        cursor.beginEditBlock()

        # iterate over all characters in the editor. remove any that aren't the
        # special replacement character. iterate backwards so that indices don't change
        for i in reversed(range(0, len(text))):

            if text[i] == self._OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

        cursor.endEditBlock()

    def eventFilter(self, object, event):
        """
        Attempts to identify clicks on one of the editor's bubble widget's
        remove button.

        :param object: The observed object.
        :type object: :class:`~PySide.QtCore.QObject`
        :param event: The event to filter.
        :type object: :class:`~PySide.QtCore.Qt.QEvent`
        :return: True'' if the event was filtered, ''False'' otherwise.
        """

        if not isinstance(event, QtGui.QMouseEvent):
            # only pass on mouse events
            return False

        # @todo:
        # can't seem to figure out how to map the viewport position to the
        # scroll area position. tried all combinations of mapto/from...
        # resulting to just adding the scroll values. please fix if you can
        edit_pos = QtCore.QPoint(
            event.pos().x() + self.horizontalScrollBar().value(),
            event.pos().y() + self.verticalScrollBar().value()
        )

        # for mouse events find the actual widget at the position
        doc = self.document()
        cursor_pos = doc.documentLayout().hitTest(edit_pos, QtCore.Qt.ExactHit)
        char_format = doc.documentLayout().format(cursor_pos)
        bubble_id = char_format.property(_BubbleTextObject.BUBBLE_DATA_PROPERTY)
        bubble = self.get_bubble(bubble_id)

        if bubble is None:
            self.viewport().setCursor(QtCore.Qt.IBeamCursor)
            return False

        self.viewport().setCursor(QtCore.Qt.ArrowCursor)

        if event.type() == QtCore.QEvent.MouseButtonPress:
            # if we are clicking on the button, do so
            bubble_pos = bubble.mapFromParent(edit_pos)
            child_widget = bubble.childAt(bubble_pos)
            if isinstance(child_widget, QtGui.QPushButton):
                child_widget.click()
            return True

        return False

    def get_bubble(self, bubble_id):
        """
        Returns a bubble widget based on the supplied id.

        The ``bubble_id`` should correspond to the unique ID returned by the
        :meth:`.add_bubble` method.

        :param bubble_id: The id of the bubble to retrieve.
        :return: A bubble widget or ``None`` if not match is found
        :rtype: :class:`.BubbleWidget`
        """

        if not bubble_id in self._char_formats:
            return None

        text = self.toPlainText()
        cursor = self.textCursor()

        # loop over each character until a replacement character with a known
        # char format that matches the supplied id is found.
        for i in xrange(0, len(text)):
            if text[i] != self._OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i+1, QtGui.QTextCursor.MoveAnchor)
            char_format = cursor.charFormat()

            if self._char_formats[bubble_id] != char_format:
                continue

            # bubble is in the text
            return self._bubble_text_object.get_bubble(bubble_id)

        return None

    def get_bubbles(self):
        """
        Similar to ``get_bubble``, but returns all bubble widgets.

        :return: List of :class:`.BubbleWidget` classes
        :rtype: list
        """

        text = self.toPlainText()
        cursor = self.textCursor()

        char_formats = []
        bubbles = []

        # find char formats for bubbles in the text editor
        for i in range(0, len(text)):
            if text[i] != self._OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i+1, QtGui.QTextCursor.MoveAnchor)
            char_format = cursor.charFormat()

            if not char_format in self._char_formats.values():
                continue

            char_formats.append(char_format)

        # get the corresponding bubbles for each found char format
        for bubble_id in self._char_formats:
            if self._char_formats[bubble_id] in char_formats:
                bubbles.append(self.get_bubble(bubble_id))

        return bubbles

    def get_typed_text(self):
        """
        Returns a :obj:`str` representing the text typed in the editor.
        """

        char_list = [c for c in self.toPlainText() if c != self._OBJECT_REPLACEMENT_CHAR]
        return "".join(char_list)

    def remove_bubble(self, bubble_id):
        """
        Remove a bubble matching the supplied id.

        :param int bubble_id: The unique id of the bubble to reomve.
        :return: The removed qt widget

        The ``bubble_id`` should correspond to the unique ID returned by the
        :meth:`.add_bubble` method.
        """

        if not self.get_bubble(bubble_id):
            return

        text = self.toPlainText()
        cursor = self.textCursor()

        # locate the bubble by iterating over each character in the editor.
        # when the match is found, remove it.
        for i in range(0, len(text)):
            if text[i] != self._OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i+1, QtGui.QTextCursor.MoveAnchor)
            char_format = cursor.charFormat()

            if self._char_formats[bubble_id] != char_format:
                continue

            # we found the bubble's object character.
            cursor.beginEditBlock()
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.endEditBlock()

            del self._char_formats[bubble_id]

            self.update()
            return


class _BubbleTextObject(QtGui.QPyTextObject):
    """
    Handles the display of bubble widgets within text documents.
    """

    BUBBLE_DATA_PROPERTY = 1
    OBJECT_TYPE = QtGui.QTextFormat.UserFormat + 1
    USING_PYQT = hasattr(QtCore, "QVariant")

    def __init__(self, parent=None):
        """
        Initialize the object.

        :param parent: This widget's parent object
        :type parent: :class:`~PySide.QtGui.QObject`
        :return:
        """
        super(_BubbleTextObject, self).__init__(parent)

        # lookup of bubble widgets by id
        self._bubbles = {}

        # count for unique ids within this instance
        self._next_id = 0

    def add_bubble(self, bubble_widget):
        """Make the object aware of this bubble widget.

        :param bubble_widget: The bubble widget to add.
        :type bubble_widget: :class:`.BubbleWidget`
        :return: The id of the added bubble
        """

        # the widget may have been added and removed

        bubble_id = self._next_id
        self._next_id += 1

        bubble_widget.id = bubble_id
        self._bubbles[bubble_id] = bubble_widget
        return bubble_id

    def clear(self):
        """Forget about all the known widgets."""
        self._bubbles = {}

    def drawObject(self, painter, rect, doc, pos_in_document, char_format):
        """Draw the appropriate widget based on the supplied char format."""

        # determine the bubble to draw
        bubble_id = char_format.property(self.BUBBLE_DATA_PROPERTY)
        bubble = self.get_bubble(bubble_id)
        bubble.setGeometry(rect.toRect())

        # now paint!
        painter.save()
        try:
            painter.translate(rect.topLeft().toPoint())

            # WEIRD! It seems pyside and pyqt actually have different signatures for this method
            if self.USING_PYQT:
                # pyqt is using the flags parameter, which seems inconsistent with QT
                # http://pyqt.sourceforge.net/Docs/PyQt4/qwidget.html#render
                bubble.render(
                    painter,
                    QtCore.QPoint(0, 1),
                    QtGui.QRegion(),
                    QtGui.QWidget.DrawChildren
                )
            else:
                # pyside is using the renderFlags parameter which seems correct
                bubble.render(
                    painter,
                    QtCore.QPoint(0, 1),
                    renderFlags=QtGui.QWidget.DrawChildren
                )
        finally:
            painter.restore()

    def get_bubble(self, bubble_id):
        """Retrieve a bubble widget for the supplied id."""

        if bubble_id in self._bubbles:
            return self._bubbles[bubble_id]

        return None

    def intrinsicSize(self, doc, pos_in_document, char_format):
        """Returns the ``sizeHint`` for the bubble widget for the supplied char format."""
        bubble_id = char_format.property(self.BUBBLE_DATA_PROPERTY)
        bubble = self.get_bubble(bubble_id)
        return bubble.sizeHint()
