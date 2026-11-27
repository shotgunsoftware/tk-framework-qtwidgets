Browser Widget
######################################

A legacy list-based browser widget with search, a busy spinner and a background
worker thread to load items and thumbnails. Items are added as ``ListItem``
(title, details and thumbnail) or ``ListHeader`` (section title) widgets.

Prefer the model/view based widgets of this framework for new development. This
module was moved from the deprecated ``tk-framework-widget`` framework so existing
apps can keep using it.

.. currentmodule:: browser_widget

.. autoclass:: BrowserWidget
    :show-inheritance:
    :members:

.. autoclass:: ListBase
    :show-inheritance:
    :members:

.. autoclass:: ListHeader
    :show-inheritance:
    :members:

.. autoclass:: ListItem
    :show-inheritance:
    :members:
