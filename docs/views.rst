View Related Classes
######################################

This module contains view classes related to QT's MVC




QT Widget Delegate System
==============================================

The widget delegates module makes it easy to create custom UI experiences that are
using data from the Shotgun Model.

If you feel that the visuals that you get back from a standard
`QTreeView` or `QListView` are not sufficient for your needs,
these view utilities provide a collection of tools to help you quickly build
consistent and nice looking user QT Views. These are typically used in conjunction
with the `ShotgunModel` but this is not a requirement.

- The `WidgetDelegate` helper class makes it easy to connect a `QWidget` of
  your choosing with a QT View. The `WidgetDelegate` will use your specified
  widget when the view is drawn and updated. This allows for full control
  of the visual appearance of any view.
- For consistency reasons we also supply a couple of simple widget classes
  that are meant to be used in conjunction with the `WidgetDelegate`. By
  using these widgets in your code you get the same look and feel as all
  other apps that use the widgets.


QT allows for customization of cell contents inside of its standard view classes through the use of so called
*delegate* classes (see http://qt-project.org/doc/qt-4.8/model-view-programming.html#delegate-classes),
however this can be cumbersome and difficult to get right. In an attempt to simplify the process of
view customization, the Shotgun Qt Widgets framework contains classes for making it easy to plugin in standard `QWidgets`
and use these as "brushes" when QT is drawing its views. You can then quickly produce UI in for example the QT designer,
hook up the data exchange between your model class and the widget in a delegate and quickly have some nice custom
looking user interfaces!

.. image:: images/widget_classes.png

The principle is that you derive a custom delegate class from the `WidgetDelegate` that is contained in the framework.
This class contains for simple methods that you need to implement. As part of this you can also control the flow of
data from the model into the widget each time it is being drawn, allowing for complex data to be easily passed from
Shotgun via the model into your widget.
For consistency, the framework also contains a number of standard widgets. Using these will provide you with a
consistent looking set of visual components.


The following example shows some of the basic around using this delegate class with the Shotgun Model::

    # import the shotgun_model and view modules from the corresponding frameworks
    shotgun_model = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
    shotgun_view = tank.platform.import_framework("tk-framework-qtwidgets", "shotgun_view")


    class ExampleDelegate(shotgun_view.WidgetDelegate):
        """
        Shows an example how to use a shotgun_view.ListWidget in a std view.
        """

        def __init__(self, view):
            """
            Constructor
            """
            shotgun_view.WidgetDelegate.__init__(self, view)

        def _create_widget(self, parent):
            """
            Returns the widget to be used when creating items
            """
            return shotgun_view.ListWidget(parent)

        def _on_before_paint(self, widget, model_index, style_options):
            """
            Called when a cell is being painted.
            """
            # extract the standard icon associated with the item
            icon = model_index.data(QtCore.Qt.DecorationRole)
            thumb = icon.pixmap(512)
            widget.set_thumbnail(thumb)

            # get the shotgun query data for this model item
            sg_item = shotgun_model.get_sg_data(model_index)

            # get values and populate widget
            version_str = "Version %03d" % sg_item.get("version_number")
            created_str = sg_item.get("created_at")
            desc_str = sg_item.get("description")
            author_str = "%s" % sg_item.get("created_by").get("name")

            header_str = "<b>%s</b>" % (version_str)
            body_str = "<b>%s</b> &mdash; %s<br><br><small>%s</small>" % (author_str, desc_str, created_str)
            widget.set_text(header_str, body_str)

        def _on_before_selection(self, widget, model_index, style_options):
            """
            Called when a cell is being selected.
            """
            # do std drawing first
            self._on_before_paint(widget, model_index, style_options)
            widget.set_selected(True)

        def sizeHint(self, style_options, model_index):
            """
            Base the size on the icon size property of the view
            """
            return shotgun_view.ListWidget.calculate_size()


The next section contains the detailed API reference for the delegate system.




WidgetDelegate
------------------------------------------

.. currentmodule:: views

.. autoclass:: WidgetDelegate
    :show-inheritance:
    :members:
    :private-members: _get_painter_widget, _create_editor_widget, _on_before_paint, _create_widget
    :exclude-members: createEditor, updateEditorGeometry, paint

EditSelectedWidgetDelegate
------------------------------------------


.. autoclass:: EditSelectedWidgetDelegate
    :show-inheritance:
    :members:
    :inherited-members:
    :private-members: _on_before_selection
    :exclude-members: createEditor, paint, updateEditorGeometry
