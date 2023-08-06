.. _usage:

How to use pydataportability.discovery
======================================

Theoretically you shouldn't have much to do but feeding a URI into
the discovery mechanism which will then return a ``Resource`` object as
defined in :mod:`pydataportability.model.resource` and explained in the
documentation of :mod:`pydataportability.xrd`.

Here is an example where we assume that the URI for discovery is stored
in ``uri``.

.. code-block:: python

    import zope.configuration.xmlconfig
    from pydataportability.discovery import discover
    
    zope.configuration.xmlconfig.file('configure.zcml', package=pydataportability.webfinger)
    
    resource = discover(uri, ['hostmeta'])    
    print "Subject: ", resource.subject
    print
    
    for link in resource.links:
        print "Rels: ", link.rels
        print "URIs:", link.uris
        print "Media Types:", link.media_types
        print "Prio:", link.priority
        print "Templates:", link.templates
        print

There are two important parts to this. The first one is the line::

    zope.configuration.xmlconfig.file('configure.zcml', package=pydataportability.discovery)

This initiates all the components used for the discovery process. It will e.g.
setup all plugins you might have defined to control the discovery process.
Usually you can use the predefined components though.

More on this can be found in the :ref:`extending` chapter.

The next important part is::

    resource = discover(uri, ['hostmeta'])

Here the discovery function is used by calling it with the URI of the resource we
want the :term:`Resource Description` for and with a list of methods to try (``hostmeta``
only in this case). Additionally you can give it a list of relationships you want it
to search for only.

.. note:: At the time of this writing only ``hostmeta`` is implemented which 
    is mainly used for :term:`WebFinger` discovery. Later we will also implement
    the remaining methods ``linkheader`` and ``link`` as defined in the 
    :term:`LRDD` specification.

This method will return an instance of 
:mod:`pydataportability.model.resource.models.Resource`. You can find a 
description of it's attributes and methods in the documentation of
:mod:`pydataportability.xrd`.

     

