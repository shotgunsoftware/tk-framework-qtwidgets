Text Overlay Widget
######################################


Introduction
======================================

.. image:: images/overlay_overview.png


The progress overlay module provides a standardized progress overlay widget which
can easily be placed on top of any other :class:`PySide.QtGui.QWidget` to indicate that work is happening
and potentially report messages back to the user. Once you have instantiated and
placed it on top of another widget, you can execute various methods to control its state.




Sample Code
--------------------------------------

The following sample code shows how to import the overlay module,
connect it to a widget and then control the overlay state::

    # example of how the overlay can be used within your app code

    # import the module - note that this is using the special
    # import_framework code so it won't work outside an app
    overlay = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")

    # now inside your app constructor, create an overlay and parent it to something
    self._overlay = overlay.ShotgunOverlayWidget(my_widget)

    # now you can use the overlay to report things to the user
    try:
       self._overlay.start_spin()
       run_some_code_here()
    except Exception, e:
       self._overlay.show_error_message("An error was reported: %s" % e)
    finally:
       self._overlay.hide()

Please note that the example above is crude and for heavy computational work we recommend
an asynchronous approach with a worker thread for better UI responsiveness.


.. currentmodule:: overlay_widget

ShotgunSpinningWidget
======================================

.. autoclass:: ShotgunSpinningWidget
    :show-inheritance:
    :members:
    :exclude-members: paintEvent

ShotgunOverlayWidget
======================================

.. autoclass:: ShotgunOverlayWidget
    :show-inheritance:
    :members:
    :inherited-members:
    :exclude-members: paintEvent

ShotgunModelOverlayWidget
======================================

.. autoclass:: ShotgunModelOverlayWidget
    :show-inheritance:
    :members:
    :exclude-members: paintEvent
