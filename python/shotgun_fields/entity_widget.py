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
from .label_base_widget import ElidedLabelBaseWidget
from .shotgun_field_meta import ShotgunFieldMeta

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class EntityWidget(ElidedLabelBaseWidget):
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
        str_val = (
            "<img src='%s'>&nbsp;<a href='%s'>%s</a>"
             % (entity_icon_url, entity_url, str_val)
        )

        return str_val


class EntityBubble(QtGui.QFrame):
    remove_clicked = QtCore.Signal(dict)

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.entity = None

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
        self.remove_clicked.emit(self.entity)

    def set_entity(self, entity_dict):
        self.entity = entity_dict
        entity_icon_url = shotgun_globals.get_entity_type_icon_url(entity_dict["type"])
        self.image_label.setText("<img src='%s'/>" % entity_icon_url)
        self.text_label.setText(entity_dict["name"])


class EntityBubbleTextObject(QtGui.QPyTextObject):
    ENTITY_PROPERTY = 1
    OBJECT_TYPE = QtGui.QTextFormat.UserFormat + 1

    USING_PYQT = hasattr(QtCore, "QVariant")

    def __init__(self, parent=None):
        QtGui.QPyTextObject.__init__(self, parent)
        self._widget_cache = {}

    def get_widget(self, entity_dict):
        if entity_dict is None:
            return None

        key = (entity_dict["type"], entity_dict["name"])
        if key in self._widget_cache:
            return self._widget_cache[key]

        self._widget_cache[key] = EntityBubble(self.parent())
        self._widget_cache[key].set_entity(entity_dict)
        self._widget_cache[key].remove_clicked.connect(self.parent().on_remove_clicked)
        return self._widget_cache[key]

    def intrinsicSize(self, doc, pos_in_document, format):
        entity_dict = format.property(self.ENTITY_PROPERTY)
        widget = self.get_widget(entity_dict)
        return widget.sizeHint()

    def drawObject(self, painter, rect, doc, pos_in_document, format):
        entity_dict = format.property(self.ENTITY_PROPERTY)
        widget = self.get_widget(entity_dict)

        widget.setGeometry(rect.toRect())

        # now paint!
        painter.save()
        try:
            painter.translate(rect.topLeft().toPoint())

            # WEIRD! It seems pyside and pyqt actually have different signatures for this method
            if self.USING_PYQT:
                # pyqt is using the flags parameter, which seems inconsistent with QT
                # http://pyqt.sourceforge.net/Docs/PyQt4/qwidget.html#render
                widget.render(
                    painter,
                    QtCore.QPoint(0, 0),
                    QtGui.QRegion(),
                    QtGui.QWidget.DrawChildren
                )
            else:
                # pyside is using the renderFlags parameter which seems correct
                widget.render(
                    painter,
                    QtCore.QPoint(0, 0),
                    renderFlags=QtGui.QWidget.DrawChildren
                )
        finally:
            painter.restore()


class EntityEditorWidget(QtGui.QTextEdit):
    __metaclass__ = ShotgunFieldMeta
    _EDITOR_TYPE = "entity"

    def setup_widget(self):
        self._formats = {}

        # XXX why crashy crashy?
        #self.entity_interface = EntityBubbleTextObject(self)
        #self.document().documentLayout().registerHandler(
        #    EntityBubbleTextObject.OBJECT_TYPE,
        #    self.entity_interface,
        #)

        #self.setMouseTracking(True)
        #self.viewport().installEventFilter(self)

        #for s in ["Bunny", "Dog", "Big Horse"]:
        #    self.insert_entity({"type": "Asset", "name": s})

    def insert_entity(self, entity_dict):
        key = (entity_dict["type"], entity_dict["name"])
        if key in self._formats:
            return

        entity_format = QtGui.QTextCharFormat()
        entity_format.setObjectType(EntityBubbleTextObject.OBJECT_TYPE)
        entity_format.setProperty(EntityBubbleTextObject.ENTITY_PROPERTY, entity_dict)
        self._formats[key] = entity_format

        orc = unichr(0xfffc)
        cursor = self.textCursor()
        cursor.insertText(orc + " ", entity_format)
        self.setTextCursor(cursor)

    def on_remove_clicked(self, entity_dict):
        print "REMOVE: %s" % entity_dict
        key = (entity_dict["type"], entity_dict["name"])
        format = self._formats.get(key)

        if format is None:
            return

        text_obj = self.document().objectForFormat(format)

    def eventFilter(self, object, event):
        if not isinstance(event, QtGui.QMouseEvent):
            # only pass on mouse events
            return False

        # for mouse events find the actual widget at the position
        doc = self.document()
        cursor_pos = doc.documentLayout().hitTest(event.pos(), QtCore.Qt.ExactHit)
        format = doc.documentLayout().format(cursor_pos)
        entity_dict = format.property(EntityBubbleTextObject.ENTITY_PROPERTY)
        widget = self.entity_interface.get_widget(entity_dict)

        if widget is None:
            self.viewport().setCursor(QtCore.Qt.IBeamCursor)
            return False

        self.viewport().setCursor(QtCore.Qt.ArrowCursor)

        if event.type() == QtCore.QEvent.MouseButtonPress:
            # if we are clicking on the button, do so
            widget_pos = widget.mapFromParent(event.pos())
            child_widget = widget.childAt(widget_pos)
            if isinstance(child_widget, QtGui.QPushButton):
                child_widget.click()

        return False

    def _display_default(self):
        pass

    def _display_value(self, value):
        # self.bubble_widget.set_entity(value)
        pass
