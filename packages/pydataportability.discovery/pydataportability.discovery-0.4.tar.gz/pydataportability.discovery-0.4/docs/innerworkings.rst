.. _innerworkings:

Implementation Details
======================

:mod:`pydataportability.discovery` is using the :term:`Zope Component Architecture`
for looking up and configuring it's components. This makes it easy to extend it without
the need to change the package itself.

First we look at how configuration is done in general and then we will look at the
components used.

Configuration
-------------

Configuration is done in `configure.zcml` files. 
:mod:`pydataportability.discovery` comes with one which you can use out of the
box without worrying about it's contents.

All you need to do to use it is to ask the :term:`Zope Component Architecture`
to configure the plugins based on this file. This is done with the following
code snippet::

    import zope.configuration.xmlconfig
    zope.configuration.xmlconfig.file('configure.zcml', package=pydataportability.discovery)
    
This imports the configuration mechanism and then tells it to use the
file ``configure.zcml`` inside the package :mod:`pydataportability.discovery`
to configure all the plugins.

This should be done in the setup phase of your application. You should not
change this configuration later on as it's meant to be defined at framework
startup time. 

After that you can then use the discovery framework by simply calling it as
described in the :ref:`usage` chapter.


What get's configured
~~~~~~~~~~~~~~~~~~~~~

In the default ``configure.zcml`` the following plugins will be defined
at the time of this writing:

 * A utility named ``acct`` which implements ``acctservice.IAcctDiscoveryService``
 * A utility named ``hostmeta`` which implements 
   ``interfaces.IDiscoveryService``.
   
This means that the discovery framework knows how to handle :term:`hostmeta discovery`
and how to handle URIs with an :term:`acct URI scheme`.

Both are needed for :term:`WebFinger` discovery which is the first use case
this discovery client implements.

A detailed explanation of how the discovery flow works and what you can plugin
where follows below.


How the discovery flow works
----------------------------

Here is a high-level overview of the components involved in discovering an XRD file:

.. image:: images/discovery-overview.png
   :width: 700px
   
What basically is happening is the following:

    1. The ``discover()`` function is called with an ``uri`` to discover the resource description for
    2. This function is iterating over all the discovery method names given in the list.
       Each of these names must be a :term:`named utility` with a type of ``IDiscoveryService``
    3. For each utility found it's ``discover()`` method is called.
    4. In case of the ``hostmeta`` discovery component it needs to find the host which it's
       delegating to another component based on the scheme of the given ``uri``. Right now
       we understand ``acct`` for webfinger URIs and ``http`` for normal HTTP URLs.
    5. In case of ``hostmeta`` the host-meta :term:`XRD` file is obtained and parsed
    6. For each link inside the document we check if it's matching a ``rel`` attribute
       the application is interested in. If so, it's ``uris`` and ``templates`` are checked
       if they are present and can be resolved.
    7. The URI of the :term:`resource document` is then found and the XRD retrieved and parsed.
    
This is the flow being used for webfinger based discovery. This also means that right now
only ``hostmeta`` is implemented, the other methods will follow later.

Resolving URI templates
~~~~~~~~~~~~~~~~~~~~~~~

Another case of pluggability is used for resolving URI templates. These templates contain
placeholders which are dependant on the ``rel`` attribute of the link they are contained in.
Thus we define a different resolver for each known ``rel`` attribute, for now this is
``http://webfinger.info/rel/service`` (webfinger) and ``describedby``. The first knows
about the ``id`` placeholder, the latter about the ``uri`` placeholder.

They both are implementing the ``IRelationshipResolver`` interface:

.. image:: images/relationships.png
   :width: 700px