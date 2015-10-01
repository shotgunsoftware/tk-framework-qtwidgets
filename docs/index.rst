The QT Widgets Framework
####################################################



The QT Widgets Framework contains a collection of QT UI Related modules.

Contents:

.. toctree::
   :maxdepth: 2

   activity_stream
   global_search_widget
   help_screen
   overlay_widget
   screen_grab
   version_label
   note_input_widget


Importing widgets into your app
=============================================

Each of the modules in this framework can be used inside your Toolkit Apps.
They are typically imported via Toolkit's special ``import_framework()`` method,
which handles automatic reload and resource management behind the scenes::

    overlay_widget = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")

These imports work just like the normal ``import`` call in python and we recommmend
that they are placed at the top of the file.

Once you have imported the module, you can access the class or objects inside::

    my_overlay = overlay.ShotgunOverlayWidget(self)


Using widgets with QT Designer
----------------------------------------------------

If you are dropping the widgets into QT Designer directly, there isn't an option to
run the ``import_framework`` method. In this case, we recommend adding imports to a wrapper
file 
