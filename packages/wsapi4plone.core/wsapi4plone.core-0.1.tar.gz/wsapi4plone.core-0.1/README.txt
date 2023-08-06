

=============================================
Web Services API for Plone (wsapi4plone.core)
=============================================

A Plone product that provides an XML-RPC API to Plone content and operations.  In other words, a Plone web services API.  One of the main goals is to provide a slim, versatile and extensive way to create, read, update and delete (CRUD) Plone content.  The secondary goal is to provide an interface on which Plone and other systems can communicate with one another.

There are five known categories that the wsapi4plone is useful for:  Cross Site Communication, Desktop Applications, Skinning/Theming, Batch Processing and Site Migration.  The primary focus of wsapi4plone thus far is on Cross Site Communication (Plone to Plone communication), Desktop Applications (Desktop Authoring) and Site Migration (Plone Import/Export)

.. contents:: Table of Contents
   :depth: 2

-------------
XML-RPC Calls
-------------

.. note:: The next version of the wsapi4plone.core package will have sphinx documentation.  The following call documentation will be derived from the view methods rather than rewriting that documentation here.  So, I ask you to please forgive any inaccuracies that may follow. Thank you.

post_object
===========

    :Usage: ``post_object(params)``
    :Input: ``{ path: [{ attr: value, ...}, type_name], ...}``
    :Returns: ``[path, ...]``
    :Example: `Post a new content object`_

put_object
==========

    :Usage: ``put_object(params)``
    :Input: ``{ path: [{ attr: value, ...}, type_name], ...}``
    :Returns: ``[path, ...]``
    :Example: `Put or update information on a content object`_

get_object
==========

    :Usage: ``get_object(path=[])``
    :Input: ``None | [path, ...]``
    :Returns: ``{ path: [{ attr: value, ...}, type_name, {misc_info: value}], ...}``
    :Example: `Get a content object`_


delete_object
=============

    :Usage: ``delete_object(path=[])``
    :Input: ``None | [path, ...]``
    :Returns: ``None``
    :Example: `Delete a content object`_

query
=====

    :Usage: ``query(filtr={})``
    :Returns: ``{ path: {index_id: value, ...}, ...}``
    :Example: `Finding what you're looking for`_

get_schema
==========

    :Usage: ``get_schema(type_name, path='')``
    :Returns: ``{ attr: {required: True | False, type: type_string, ...}, ...}``
    :Example: `Get a content object's structure`_

get_types
=========

    :Usage: ``get_types(path='')``
    :Returns: ``[[type_id, type_title], ...]``
    :Example: `Get the available content-types`_

get_workflow
============

    :Usage: ``get_workflow(path='')``
    :Returns: ``{ state: current_state, transitions: [transition_name, ...], ...}``
    :Example: `Get a content object's workflow state`_

set_workflow
============

    :Usage: ``set_workflow(transition, path='')``
    :Returns: ``None``
    :Example: `Transition a content object's workflow state`_

get_discussion
==============

    :Usage: ``get_discussion(path='')``
    :Returns:

    ::

        {'id': {'in_reply_to': 'another_id',
                'title': '',
                'text': '',
                'cooked_text': '',
                'created': '2009-11-03 12:12:59',
                'creators': ()
                }, ...
         }

    :Example: `Get a content object's discussion container`_

------------------------------
Installation (for zc.buildout)
------------------------------

To install wsapi4plone simply add the following lines to your Plone instance declaration.  The next time you start Zope the calls will be available.  No further installation is required.
::

    ...
    eggs =
        ...
        wsapi4plone.core
    zcml =
        ...
        wsapi4plone.core
