Navigation Widgets
######################################

The navigation module contains standard widgets that can
be used to track navigation and state.

.. image:: images/navigation.png

The breadcrumbs widget is a standard widget that displays a history
of things separated by arrows. This class utilizes the :class:`~elided_label.ElidedLabel` widget
to ensure that names are reduced down nicely in the case there ins't enough
space to display the entire history.

The navigation widget implements the standard home/next/prev concept that can be
found in several Toolkit apps.


Breadcrumbs
======================================

.. currentmodule:: navigation

.. autoclass:: BreadcrumbWidget
    :show-inheritance:
    :members:

.. autoclass:: Breadcrumb
    :members:

Home/Next/Prev Navigation
======================================

.. autoclass:: NavigationWidget
    :show-inheritance:
    :members:
