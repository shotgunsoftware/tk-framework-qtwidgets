############
Introduction
############

**Server API - for making changes and for complex searches**

The server API connects to a database storage. When you perform an operation
on the ``tank.server`` API, the system will connect to a database and query the database
for information.

The server API also lets you manipulate data, either by deleting, updating or creating it.

.. note::

	To quickly just get a label, asset or revision object from its address, just
	do a ``tank.server.find("address")``


Caching Policy
==============
All objects returned by the server API are being disconnected from their source when
they leave the API. Any changes made to the data is not reflected in any returned objects.


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
