.. _extending:

Extending and configuring the discovery process
===============================================

The discovery process is highly configurable by various plugins which are
configured using the :term:`Zope Component Architecture`.


How to configure plugins
~~~~~~~~~~~~~~~~~~~~~~~~

If you look at the ``configure.zcml`` file you can see entries such as this one:

.. code-block:: xml

    <utility
        provides=".interfaces.IDiscoveryService"
        factory=".hostmeta.HostMetaDiscoveryService"
        name="hostmeta"
        />

This entry defines a utility which implements the interface 
``.interfaces.IDiscoveryService``. It's implementation can be found at
``.hostmeta.HostMetaDiscoveryService`` and it's configured under the name
``hostmeta``. Thus we call it a :term:`named utility`.



Extension points in the main flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the main flow you can easily plugin your own discovery plugins by
implementing one which provides the ``pydataportability.discovery.interfaces.IDiscoveryService``
interface. Give it a separate name and create your own ``configure.zcml`` file
by copying the original one and adding a new entry for your utility.

Then you can list the name of your ``IDiscoveryService`` utility inside
the call to the discovery client.

The discovery flow inside the ``hostmeta`` discovery service
------------------------------------------------------------

The named utility of type ``IDiscoveryService`` and name ``hostmeta``
will first split the URI into it's elements and will then try to obtain
a handler for the URI scheme it found. In the :term:`Webfinger` case it would
find the ``acct:`` scheme. 

The handler is again obtained by querying for a named utility implementing
the necessary logic. In the ``acct:`` case a named utility implementing
``IHostMetaSchemaHandler`` and with ``acct`` as name. This handler is then 
responsible for extracting the host from the URI and return it to the
actual ``hostmeta`` handler.

The ``hostmeta`` handler will then obtain the host-meta file from this host and
try to obtain the location of the :term:`Resource Description` of the original URI.







