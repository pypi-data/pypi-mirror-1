.. _glossary:

============================
Glossary
============================

.. glossary::

  XRD
    `XRD <http://www.oasis-open.org/committees/download.php/34072/xrd-1.0-wd06.html>`_ 
    stands for "eXtensible Resource Descriptor"
  Webfinger
    Webfinger is a proposal for a protocol for defining account identifiers and obtaining
    resources for this account. It is defined on `Google Code 
    <http://code.google.com/p/webfinger/>`_ and  discussed in the 
    `WebFinger Google Group <http://groups.google.com/group/webfinger>`_.
  Virtualenv
    An isolated Python environment.  Allows you to control which
    packages are used on a particular project by cloning your main
    Python.  `virtualenv <http://pypi.python.org/pypi/virtualenv>`_
    was created by Ian Bicking.
  Setuptools
    `Setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    builds on Python's ``distutils`` to provide easier building,
    distribution, and installation of libraries and applications.
  LRDD
    ``LRDD`` stands for `Link-based Resource Descriptor Discovery`. More 
    information on it can be found on `this post by Eran Hammer-Lahav 
    <http://hueniverse.com/2009/03/the-discovery-protocol-stack/>`_. It also
    describes the relationship to :term:`XRD` and the three possible
    discovery methods.
  Resource Description
    A Resource Description document is a description of an actual resource,
    e.g. a web document or a user account defined by an URI. For a user
    account it can e.g. contain links to other resources of that user.
  Zope Component Architecture    
    The `Zope Component Architecture
    <http://www.muthukadan.net/docs/zca.html>`_ (aka ZCA) is a system
    which allows for application pluggability and complex dispatching
    based on objects which implement an :term:`interface`.
  Interface
    A `Zope interface <http://pypi.python.org/pypi/zope.interface>`_
    object.  In :mod:`pydataportability.discovery`, interfaces are used
    to identify plugins. You can think of it as something like a type
    for a component. 
    You can use the :term:`Zope Component Architecture` to look components
    up by their interface and optionally with an additonal name.
  acct URI scheme
    The proposed ``acct:`` URI scheme was invented by the :term:`Webfinger`
    group. It is meant as a format for email-like user identifiers such as
    ``acct:joe@foobar.com``. Compared to ``mailto:`` is has a different
    semantic meaning as it's not meant to be used for sending mail but
    to simply identify a single user on a specific host. In :term:`Webfinger`
    it is used as a URI on which discovery is taking place, resulting in a
    :term:`Resource Description` document with more pointers to the user's
    resources stored elsewhere. For more information consult the
    :term:`Webfinger` discussion group and wiki.
  Utility
    A utility is one of the component types the :term:`Zope Component Architecture`
    defines. It is usually a class implementing a utility function which
    can be identified by an interface it implements. It is a global object
    (singleton) which can be retrieved by it's interface. This makes it possible
    to replace utilities being used in a framework in your own code by
    simply registering your utility instead of the framework one. This omit
    changes to the framework.
  named utility
    A Named Utility is a :term:`Utility` which additional to it's :term:`Interface`
    is identified also by name. This way you can provide different utilities
    for the same :term:`Interface` with different names as it's done in
    :mod:`pydataportability.discovery` where you can have various utilities
    implementing ``IDiscoveryService`` with different names which can also have
    their try on finding a :term:`Resource Description`.
    