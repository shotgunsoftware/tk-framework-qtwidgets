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


class BubbleEditWidget(QtGui.QTextEdit):

    OBJECT_REPLACEMENT_CHAR = unichr(0xfffc)

    def __init__(self, parent=None):

        super(BubbleEditWidget, self).__init__(parent)

        self._formats = {}

        self._bubble_text_object = BubbleTextObject(self)
        self.document().documentLayout().registerHandler(
            BubbleTextObject.OBJECT_TYPE, self._bubble_text_object,
        )

        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)

    def clear(self):
        for format in self._formats.values():
            del format
        self._bubble_text_object.clear()
        super(BubbleEditWidget, self).clear()

    def add_bubble(self, bubble):

        bubble_id = self._bubble_text_object.add_bubble(bubble)

        format = QtGui.QTextCharFormat()
        format.setObjectType(self._bubble_text_object.OBJECT_TYPE)
        format.setProperty(self._bubble_text_object.BUBBLE_DATA_PROPERTY, bubble_id)
        self._formats[bubble_id] = format

        bubble.remove_clicked.connect(
            lambda: self.on_remove_clicked(bubble_id)
        )

        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.insertText(self.OBJECT_REPLACEMENT_CHAR, format)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

        return bubble_id

    def on_remove_clicked(self, bubble_id):
        self.remove_bubble(bubble_id)

    def remove_bubble(self, bubble_id):

        if not self.get_bubble(bubble_id):
            return

        text = self.toPlainText()
        cursor = self.textCursor()

        for i in range(0, len(text)):
            if not text[i] == self.OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i+1, QtGui.QTextCursor.MoveAnchor)
            format = cursor.charFormat()

            if not self._formats[bubble_id] == format:
                continue

            # we found the bubble's object character.
            cursor.beginEditBlock()
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.endEditBlock()

            del self._formats[bubble_id]

            self.update()
            return

    def get_bubble(self, bubble_id):

        if not bubble_id in self._formats:
            return None

        text = self.toPlainText()
        cursor = self.textCursor()

        for i in range(0, len(text)):
            if not text[i] == self.OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i+1, QtGui.QTextCursor.MoveAnchor)
            format = cursor.charFormat()

            if not self._formats[bubble_id] == format:
                continue

            # bubble is in the text
            return self._bubble_text_object.get_bubble(bubble_id)

        return None

    def get_bubbles(self):

        text = self.toPlainText()
        cursor = self.textCursor()

        formats = []
        bubbles = []

        # find formats for bubbles in the text editor
        for i in range(0, len(text)):
            if not text[i] == self.OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i+1, QtGui.QTextCursor.MoveAnchor)
            format = cursor.charFormat()

            if not format in self._formats.values():
                continue

            formats.append(format)

        # get the corresponding bubbles for each found format
        for bubble_id in self._formats:
            if self._formats[bubble_id] in formats:
                bubbles.append(self.get_bubble(bubble_id))

        return bubbles

    def clear_typed_text(self):

        text = self.toPlainText()
        cursor = self.textCursor()

        cursor.beginEditBlock()

        # iterate backwards so that indices don't change
        for i in reversed(range(0, len(text))):

            if text[i] == self.OBJECT_REPLACEMENT_CHAR:
                continue

            cursor.setPosition(i, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

        cursor.endEditBlock()

    def get_typed_text(self):

        char_list = [c for c in self.toPlainText() if c != self.OBJECT_REPLACEMENT_CHAR]
        return  "".join(char_list)

    def eventFilter(self, object, event):
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
        format = doc.documentLayout().format(cursor_pos)
        bubble_id = format.property(BubbleTextObject.BUBBLE_DATA_PROPERTY)
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

        return False


class BubbleWidget(QtGui.QFrame):

    remove_clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super(BubbleWidget, self).__init__(parent)

        self._data = None

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        self.setObjectName("bubble")
        self.setStyleSheet(
            """
            #bubble {
                border: 1px solid black;
                border-radius: 5px;
                background-color: %s;
            } """ % self.palette().color(QtGui.QPalette.Button).name()
        )

        self.remove_button = QtGui.QPushButton(self)
        style = self.remove_button.style()
        icon = style.standardIcon(style.SP_TitleBarCloseButton)
        self.remove_button.setIcon(icon)
        self.remove_button.setFlat(True)
        self.remove_button.setStyleSheet("border: none")

        self.image_label = QtGui.QLabel(self)

        text_color = QtGui.QColor(
            sgtk.constants.SG_STYLESHEET_CONSTANTS["SG_HIGHLIGHT_COLOR"]
        )
        self.text_label = QtGui.QLabel(self)
        palette = self.text_label.palette()
        palette.setColor(QtGui.QPalette.WindowText, text_color)
        self.text_label.setPalette(palette)

        self.layout = QtGui.QHBoxLayout()
        self.layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.layout.setContentsMargins(3, 1, 3, 1)
        self.layout.setSpacing(2)

        self.layout.addWidget(self.image_label, QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.text_label, QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.remove_button, QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout)

        self.remove_button.clicked.connect(
            lambda: self.remove_clicked.emit()
        )

    def set_text(self, label_text):
        self.text_label.setText(label_text)

    def set_image(self, url):
        self.image_label.setText("<img src='%s'/>" % url)

    def set_removable(self, removable):
        if removable:
            self.remove_button.show()
        else:
            self.remove_button.hide()

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data


class BubbleTextObject(QtGui.QPyTextObject):

    BUBBLE_DATA_PROPERTY = 1
    OBJECT_TYPE = QtGui.QTextFormat.UserFormat + 1
    USING_PYQT = hasattr(QtCore, "QVariant")

    def __init__(self, parent=None):
        super(BubbleTextObject, self).__init__(parent)
        self._bubbles = {}

        self._next_id = 0

    def clear(self):
        self._bubbles = {}

    def add_bubble(self, bubble_widget):

        # the widget may have been added and removed

        bubble_id = self._next_id
        self._next_id += 1

        bubble_widget.id = bubble_id
        self._bubbles[bubble_id] = bubble_widget
        return bubble_id

    def get_bubble(self, bubble_id):

        if bubble_id in self._bubbles:
            return self._bubbles[bubble_id]

        return None

    def intrinsicSize(self, doc, pos_in_document, format):
        bubble_id = format.property(self.BUBBLE_DATA_PROPERTY)
        bubble = self.get_bubble(bubble_id)
        return bubble.sizeHint()

    def drawObject(self, painter, rect, doc, pos_in_document, format):

        bubble_id = format.property(self.BUBBLE_DATA_PROPERTY)
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

