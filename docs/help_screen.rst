############
Introduction
############




Tank Publishing Classes
==============================================

The following sections outlines and demonstrates all the various items which can be created in tank.
The principle to create something in tank is the same for all types of objects; instantiate a Publisher
object, specify the necessary parameters for the object and then publish it. THe publish method will
carry out the necessary transactions and operations and once this function completes, the object
exists in the tank system.

The publishing process is introspective, meaning that its possible to query a publishing object
for its required or optional parameters. The publisher can also be used to validate values to make
sure that they are in the correct range, follow the correct naming conventions etc. All publishers
share the same interface - so the code to create a new label is rougly the same
as the code to create a new revision.




.. currentmodule:: help_screen

.. autofunction:: show_help_screen

