Model Related Classes
######################################

The ``models`` module contains QT Models and model related classes that
are useful when building MVC setups and when you need to filter data in
various ways.


HierarchicalFilteringProxyModel
======================================

.. currentmodule:: models

.. autoclass:: HierarchicalFilteringProxyModel
    :show-inheritance:
    :members: _is_row_accepted, enable_caching
    :private-members: _is_row_accepted

ShotgunSortFilterProxyModel
======================================

.. currentmodule:: models

.. autoclass:: ShotgunSortFilterProxyModel
    :show-inheritance:
    :members: lessThan, filterAcceptsRow
    :private-members: _get_processable_field_data
