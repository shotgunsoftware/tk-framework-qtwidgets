Shotgun Search Completers
#############################################


.. currentmodule:: search_completer


Global Search Completer
=======================

The global search completer is a QCompleter instance for use with widgets
that allow input of Shotgun entities. The completer can be customized to 
search across a given set of entity types. 

Once a user selects an object, a signal fires to indicate that an entity
was activated.

.. autoclass:: GlobalSearchCompleter
    :members:
    :inherited-members:


Hierarchical Search Completer
=============================

The hierarchical search completer is a QCompleter instance for use with widgets
that allow input of Shotgun entities. The completer can be customized to search
in a site's complete hierarchy or in a single project.

Once a user selects an object, a signal fires to indicate that a node from the
hierarchy was selected.

.. autoclass:: HierarchicalSearchCompleter
    :members:
    :inherited-members: