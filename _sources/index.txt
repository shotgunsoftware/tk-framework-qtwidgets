The QT Widgets Framework
####################################################

The QT Widgets Framework contains a collection of QT UI Related modules.

Contents:

.. toctree::
   :maxdepth: 2

   activity_stream
   elided_label
   search_completer
   shotgun_search_widget
   context_widget
   help_screen
   models
   navigation
   note_input_widget
   overlay_widget
   playback_label
   screen_grab
   shotgun_fields
   shotgun_menus
   spinner_widget
   version_details
   views

Importing widgets into your app
=============================================

Each of the modules in this framework can be used inside your Toolkit Apps.
They are typically imported via Toolkit's special ``import_framework()`` method,
which handles automatic reload and resource management behind the scenes::

    overlay_widget = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")

These imports work just like the normal ``import`` call in python and we recommend
that they are placed at the top of the file.

Once you have imported the module, you can access the class or objects inside::

    my_overlay = overlay.ShotgunOverlayWidget(self)

.. _widgets-in-designer:

Using widgets with QT Designer
----------------------------------------------------

If you are dropping the widgets into QT Designer directly, there isn't an option to
run the ``import_framework`` method. In this case, we recommend adding imports to a wrapper
file and place that next to your other python files. You can for example call this file
``qtwidgets.py`` and then do the imports in this file::

    import sgtk

    note_input_widget = sgtk.platform.current_bundle().import_module("note_input_widget")
    NoteInputWidget = note_input_widget.NoteInputWidget

    version_label = sgtk.platform.current_bundle().import_module("version_label")
    VersionLabel = version_label.VersionLabel

In your designer generated ``.ui`` files, you can now reference these widgets as if they were
local to your project.
