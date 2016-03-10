# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Widget that represents the value of an entity field in Shotgun
"""
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .label_base_widget import LabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class EntityWidget(LabelBaseWidget):
    """
    Inherited from a :class:`~LabelBaseWidget`, this class is able to
    display an entity field value as returned by the Shotgun API.
    """
    __metaclass__ = ShotgunFieldMeta
    _DISPLAY_TYPE = "entity"

    def _string_value(self, value):
        """
        Convert the Shotgun value for this field into a string

        :param value: The value to convert into a string
        :type value: A Shotgun entity dictionary containing at least keys for type, int, and name
        """
        return self._entity_dict_to_html(value)

    def _entity_dict_to_html(self, value):
        """
        Translate the entity dictionary to html that can be displayed in a
        :class:`~PySide.QtGui.QLabel`.

        :param value: The entity dictionary to convert to html
        :type value: An entity dictionary containing at least the name, type, and id keys
        """
        str_val = value["name"]

        if self._bundle.sgtk.shotgun_url.endswith("/"):
            url_base = self._bundle.sgtk.shotgun_url
        else:
            url_base = "%s/" % self._bundle.sgtk.shotgun_url

        entity_url = "%sdetail/%s/%d" % (url_base, value["type"], value["id"])
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(value["type"])
        str_val = "<img src='%s'><a href='%s'>%s</a>" % (entity_icon_url, entity_url, str_val)
        return str_val


class EntityBubble(QtGui.QFrame):
    remove_clicked = QtCore.Signal()

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        self.setObjectName("bubble")
        self.setStyleSheet(
            """
            #bubble {
                border: 1px solid black;
                background-color: %s; border-radius: 5px;
            }
            """ % sgtk.constants.SG_STYLESHEET_CONSTANTS["SG_HIGHLIGHT_COLOR"])

        self.close_button = QtGui.QPushButton(self)
        style = self.close_button.style()
        icon = style.standardIcon(style.SP_TitleBarCloseButton)
        self.close_button.setIcon(icon)
        self.close_button.setFlat(True)
        self.close_button.setStyleSheet("border: none")

        self.image_label = QtGui.QLabel(self)
        self.text_label = QtGui.QLabel(self)

        self.layout = QtGui.QHBoxLayout()
        self.layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.layout.setContentsMargins(3, 1, 3, 1)
        self.layout.setSpacing(2)

        self.layout.addWidget(self.image_label, QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.text_label, QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.close_button, QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout)

        self.close_button.clicked.connect(self._on_close_button_clicked)

    def _on_close_button_clicked(self):
        self.remove_clicked.emit()
        print "CLOSE"

    def set_entity(self, entity_dict):
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(entity_dict["type"])
        self.image_label.setText("<img src='%s'/>" % entity_icon_url)
        self.text_label.setText(entity_dict["name"])


class EntityEditorWidget(QtGui.QLineEdit):
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "entity"

    def setup_widget(self):
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.container = QtGui.QFrame(self)
        self.container_layout = FlowLayout(self)
        self.container_layout.setContentsMargins(3, 3, 3, 3)
        self.container.setLayout(self.container_layout)
        self.container.show()
        self.container.setGeometry(3, 3, self.width() - 3, self.height() - 3)

        for s in ["Bunny", "Dog", "Big Horse"]:
            b = EntityBubble(self.container)
            b.set_entity({"type": "Asset", "name": s})
            self.container_layout.addWidget(b)

    def resizeEvent(self, event):
        self.container.setGeometry(3, 3, self.width() - 3, self.height() - 3)
        QtGui.QLineEdit.resizeEvent(self, event)

    def focusInEvent(self, event):
        last_item = self.container_layout.itemAt(self.container_layout.count() - 1)
        geo = last_item.geometry()

        margins = self.textMargins()
        margins.setLeft(geo.right() + 5)
        margins.setTop(geo.top())
        self.setTextMargins(margins)

        QtGui.QLineEdit.focusInEvent(self, event)

    def _display_default(self):
        pass

    def _display_value(self, value):
        # self.bubble_widget.set_entity(value)
        pass


class FlowLayout(QtGui.QLayout):
    def __init__(self, parent=None):
        super(FlowLayout, self).__init__(parent)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        try:
            return self.itemList[index]
        except IndexError:
            return None

    def takeAt(self, index):
        try:
            return self.itemList.pop(index)
        except IndexError:
            return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()