Shotgun Field Widgets
#####################

Introduction
============

The ``shotgun_fields`` module provides access to Qt widgets that correspond
to the field types available on Shotgun entities. The purpose of these widgets
is to make it easier to build apps that interact with Shotgun in a standardized
way.

.. image:: images/shotgun_fields.png

----

Field Widget Manager
====================

Access to individual field widgets is provided by the :class:`.ShotgunFieldManager`
factory class via the ``create_widget()`` method. Additional convenience methods
are avaialble on the class for creating delegates and labels corresponding to the
supplied Shotgun entity type and field.

.. currentmodule:: shotgun_fields

.. autoclass:: ShotgunFieldManager
    :show-inheritance:
    :members:

----

Field Widget Metaclass
======================

All field widgets use the :class:`.ShotgunFieldMeta` class as their ``__metaclass__``
in order to provide a consistent API across widgets of different types and to
register imported classes with the :class:`.ShotgunFieldManager`.

.. currentmodule:: shotgun_fields.shotgun_field_meta

.. autoclass:: ShotgunFieldMeta
    :show-inheritance:
    :exclude-members: get_value, set_value, setup_widget, take_over_if_not_defined

----

Field Widgets
=============

The following is a list of all of the widgets available by default via the
:class:`.ShotgunFieldManager`. Instances of these classes are created by calling
the manager's ``create_widget()`` method.

----

Checkbox
--------

The ``CheckBoxWidget`` class serves as both editor and display for ``checkbox``
field types in Shotgun. When requested as a ``DISPLAY`` type from a field manager
instance, the returned widget will simply be disabled.

.. image:: images/field_checkbox.png

.. currentmodule:: shotgun_fields.checkbox_widget

.. autoclass:: CheckBoxWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget

----

Currency
--------

.. image:: images/field_currency.png

.. currentmodule:: shotgun_fields.currency_widget

.. autoclass:: CurrencyWidget
    :show-inheritance:
    :members:

.. autoclass:: CurrencyEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Date And Time
-------------

.. image:: images/field_datetime.png

.. currentmodule:: shotgun_fields.date_and_time_widget

.. autoclass:: DateAndTimeWidget
    :show-inheritance:
    :members:

.. autoclass:: DateAndTimeEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Date
----

.. image:: images/field_date.png

.. currentmodule:: shotgun_fields.date_widget

.. autoclass:: DateWidget
    :show-inheritance:
    :members:

.. autoclass:: DateEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Duration
--------

.. note::

    There are no widgets available for the ``duration`` field yet since there
    is not yet API support for display options like hours vs. days, numbers of
    hours in a workday, etc.

----

Entity
------

.. image:: images/field_entity.png

.. currentmodule:: shotgun_fields.entity_widget

.. autoclass:: EntityWidget
    :show-inheritance:
    :members:

.. autoclass:: EntityEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget

----

File Link
---------

.. image:: images/field_file_link.png

.. currentmodule:: shotgun_fields.file_link_widget

.. autoclass:: FileLinkWidget
    :show-inheritance:
    :members:
    :exclude-members: eventFilter

----

Float
-----

.. image:: images/field_float.png

.. currentmodule:: shotgun_fields.float_widget

.. autoclass:: FloatWidget
    :show-inheritance:
    :members:

.. autoclass:: FloatEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Footage
-------

.. image:: images/field_footage.png

.. currentmodule:: shotgun_fields.footage_widget

.. autoclass:: FootageWidget
    :show-inheritance:
    :members:

.. autoclass:: FootageEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Image
-----

.. image:: images/field_image.png

.. currentmodule:: shotgun_fields.image_widget

.. autoclass:: ImageWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget, eventFilter, heightForWidth, minimumSizeHint, resizeEvent, setPixmap, sizeHint

----

List
----

.. image:: images/field_list.png

.. currentmodule:: shotgun_fields.list_widget

.. autoclass:: ListWidget
    :show-inheritance:
    :members:

.. autoclass:: ListEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget

----

Multi Entity
------------

.. image:: images/field_multi_entity.png

.. currentmodule:: shotgun_fields.multi_entity_widget

.. autoclass:: MultiEntityWidget
    :show-inheritance:
    :members:

.. autoclass:: MultiEntityEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget, focusInEvent, hideEvent, keyPressEvent,

----

Number
------

.. image:: images/field_number.png

.. currentmodule:: shotgun_fields.number_widget

.. autoclass:: NumberWidget
    :show-inheritance:
    :members:

.. autoclass:: NumberEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Percent
-------

.. image:: images/field_percent.png

.. currentmodule:: shotgun_fields.percent_widget

.. autoclass:: PercentWidget
    :show-inheritance:
    :members:

.. autoclass:: PercentEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Status List
-----------

.. image:: images/field_status_list.png

.. currentmodule:: shotgun_fields.status_list_widget

.. autoclass:: StatusListWidget
    :show-inheritance:
    :members:

.. autoclass:: StatusListEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget

----

Tags
----

.. image:: images/field_tags.png

.. currentmodule:: shotgun_fields.tags_widget

.. autoclass:: TagsWidget
    :show-inheritance:
    :members:

.. note::

    There is no editor widget for ``tags`` because the python API does
    not currently support editing fields of this type.

----

Text
----

.. image:: images/field_text.png

.. currentmodule:: shotgun_fields.text_widget

.. autoclass:: TextWidget
    :show-inheritance:
    :members:

.. autoclass:: TextEditorWidget
    :show-inheritance:
    :members:
    :exclude-members: keyPressEvent, setup_widget

----

Timecode
--------

.. note::

    There are no widgets available for the ``timecode`` field yet since there
    is not yet API support for an associated ``fps`` field.

----

Url Template
------------

.. image:: images/field_url_template.png

.. currentmodule:: shotgun_fields.url_template_widget

.. autoclass:: UrlTemplateWidget
    :show-inheritance:
    :members:

.. note::

    There is no editor widget for ``url_templates`` because the python API does
    not currently support editing fields of this type.

----

Editable Widgets
================

Requesting the ``EDITABLE`` type for a field via the manager will return a
``ShotgunFieldEditable`` instance. This widget is a stacked widget that includes
both the display and editor currency widgets. You can see examples of the
editable widgets at the bottom of each screenshot above.

Clicking on the pencil icon while hovering over the display widget will swap
the display widget for the editor. When the editor is visible, clicking the
``X`` icon will switch back to the display widget and revert any changes made
in the editor. If the check mark icon is clicked, the changes will be applied
and the the display widget will be shown with the new value.

.. currentmodule:: shotgun_fields.shotgun_field_editable

.. autoclass:: ShotgunFieldEditable
    :show-inheritance:
    :members:
    :exclude-members: minimumSizeHint, sizeHint

If an ``EDITABLE`` type is requested for a field that has no registered editor
widget, then an instance of ``ShotgunFieldNotEditable`` will be returned. This
class displays the editor with an additional icon when hovered that indicates
that the field is not editable.

.. autoclass:: ShotgunFieldNotEditable
    :show-inheritance:
    :members:
    :exclude-members: eventFilter

----

Base Classes
============

The following classes are used as base classes in one or more field widgets and
may prove useful when diving into the details of a widget's implementation.

Bubble Edit Widget
------------------

.. currentmodule:: shotgun_fields.bubble_widget

The ``BubbleEditWidget`` class is used as a base class for editing a list of
objects. The :class:`.MultiEntityEditorWidget` is a subclass of the
``BubbleEditWidget``.

.. autoclass:: BubbleEditWidget
    :show-inheritance:
    :members:
    :exclude-members: eventFilter

----

Bubble Widget
-------------

This class represents individual "bubbles" managed within a ``BubbleEditWidget``
subclasses.

.. autoclass:: BubbleWidget
    :show-inheritance:
    :members:

----

Label Base Widget
-----------------

The ``LabelBaseWidget`` provides a very simple base class for many of the display
widgets above. It provides the basic interface required by classes using the
:class:`.ShotgunFieldMeta` ``__metaclass__``.

.. currentmodule:: shotgun_fields.label_base_widget

.. autoclass:: LabelBaseWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget

----

Elided Label Base Widget
------------------------

The ``ElidedLabelBaseWidget`` is nearly identical to the ``LabelBaseWidget``
except that it will elide its display text when the text is too long to display
in the layout.

.. autoclass:: ElidedLabelBaseWidget
    :show-inheritance:
    :members:
    :exclude-members: setup_widget

----

Field Widget Delegates
======================

.. currentmodule:: shotgun_fields.shotgun_field_delegate

.. autoclass:: ShotgunFieldDelegate
    :show-inheritance:
    :members:

----

Example Code
============

.. code-block:: python
    :linenos:
    :caption: Populate a QTableWidget with the results of a Shotgun query
    :emphasize-lines: 9-11,39-40

    class ExampleTableWidget(QtGui.QWidget):
        def __init__(self):
            QtGui.QWidget.__init__(self)

            # grab the current app bundle for use later
            self._app = sgtk.platform.current_bundle()

            # initialize the field manager
            self._fields_manager = shotgun_fields.ShotgunFieldManager(self)
            self._fields_manager.initialized.connect(self.populate_dialog)
            self._fields_manager.initialize()

        def populate_dialog(self):
            entity_type = "Version"
            entity_query = []

            # grab all of the fields on the entity type
            fields = sorted(self._app.shotgun.schema_field_read(entity_type).keys())

            # query Shotgun for the entities to display
            entities = self._app.shotgun.find(entity_type, entity_query, fields=fields)

            # set the headers for each field
            field_labels = []
            for field in fields:
                field_labels.append(shotgun_globals.get_field_display_name(entity_type, field))

            # create the table that will display all the data
            table = QtGui.QTableWidget(len(entities), len(fields), self)
            table.setHorizontalHeaderLabels(field_labels)

            # create display widgets only
            widget_type = self._fields_manager.DISPLAY

            # populate the table with the data in the entities returned by the query above
            for (i, entity) in enumerate(entities):
                for (j, field) in enumerate(fields):
                    # create the widget for each field
                    widget = self._fields_manager.create_widget(
                        entity_type, field, widget_type, entity)
                    if widget is None:
                        # backup in case the manager does not understand this field type
                        widget = QtGui.QLabel("No widget")

                    # put the widget into the table
                    table.setCellWidget(i, j, widget)

            # update widths and setup the table to be displayed
            table.resizeColumnsToContents()
            layout = QtGui.QVBoxLayout(self)
            layout.addWidget(table)
            self.setLayout(layout)

.. code-block:: python
    :linenos:
    :caption: Display data from a ShotgunModel in a TableView
    :emphasize-lines: 6-8,15,21

    class ExampleTableView(QtGui.QWidget):
        def __init__(self):
            QtGui.QWidget.__init__(self)

            # grab a field manager to get the delegate
            self.fields_manager = shotgun_fields.ShotgunFieldManager(self)
            self.fields_manager.initialized.connect(self.on_initialized)
            self.fields_manager.initialize()

        def on_initialized(self):
            entity_type = "Version"

            # grab all displayable fields on the entity type, with "code" first
            fields = shotgun_globals.get_entity_fields(entity_type)
            fields = self.fields_manager.supported_fields(entity_type, fields)
            fields = ["code"] + [f for f in fields if f != "code"]

            # setup the model and view
            self.model = shotgun_model.SimpleShotgunModel(self)
            self.model.load_data(entity_type, filters=[], fields=fields, columns=fields)
            self.table = views.ShotgunTableView(self.fields_manager, parent=self)
            self.table.setModel(self.model)

            # and layout the dialog
            layout = QtGui.QVBoxLayout(self)
            layout.addWidget(self.table)
            self.setLayout(layout)

TODOs & Known Issues
====================

- Bubble widget does not display characters properly in some scenarios
- Timecode & Duration widgets are on hold until python API changes make them feasible
- Tag edit widget partially done but also awaiting python API edit ability
- ``ElidedLabel`` causes draw lagging when used in editable widget in Grid/Form layout
- The note input widget should be updated to use the global completer
- The status list widget editor should also use colors for visual hint like display widget
- shotgun model to auto update SG on changes still to come
