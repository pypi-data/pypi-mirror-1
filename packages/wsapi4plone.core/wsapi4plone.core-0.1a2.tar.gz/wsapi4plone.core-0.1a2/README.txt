

=============================================
Web Services API for Plone (wsapi4plone.core)
=============================================

A Plone product that provides an XML-RPC API to Plone content and operations.  In other words, a Plone web services API.  One of the main goals is to provide a slim, versatile and extensive way to create, read, update and delete (CRUD) Plone content.  The secondary goal is to provide an interface on which Plone sites can communicate with one another.

There are five categories that the wsapi4plone could be useful for:  Cross Site Communication, Desktop Applications, Skinning/Theming, Batch Processing and Site Migration.  The primary focus of wsapi4plone thus far is on Cross Site Communication (Plone to Plone communication), Desktop Applications (Desktop Authoring) and Site Migration (Plone Import/Export).  

XML-RPC Calls
-------------

* ``post_object(params)``
    input: ``{ path: [{ attr: value, ...}, type_name], ...}``
    returns: ``[path, ...]``

* ``put_object(params)``
    input: ``{ path: [{ attr: value, ...}, type_name], ...}``
    returns: ``[path, ...]``

* ``get_object(paths=[])``
    input: ``[path, ...]``
    returns: ``{ path: [{ attr: value, ...}, type_name, {misc}], ...}``

* ``delete_object(paths=[])``
    input: ``[path, ...]``
    returns: None

* ``query(filtr={})``
    returns: ``{ path: {index_id: value, ...}, ...}``

* ``clipboard(action, target, destination)``
    Not Yet Implemented

* ``get_schema(type_name, path='')``
    returns: ``{ attr: {required: True | False, type: type_string, ...}, ...}``

* ``get_types(path='')``
    returns: ``[type_name, ...]``

* ``get_workflow(path='')``
    returns: ``{ state: current_state, transitions: [transition_name, ...], ...}``

* ``set_workflow(transition, path='')``
    returns: None

Installation
------------
To install wsapi4plone, simply add the following lines to your Plone instance declaration.  The next time you start Zope, the calls will be available.  No further installation is required.
::

    ...
    eggs =
        ...
        wsapi4plone.core
    zcml =
        ...
        wsapi4plone.core
