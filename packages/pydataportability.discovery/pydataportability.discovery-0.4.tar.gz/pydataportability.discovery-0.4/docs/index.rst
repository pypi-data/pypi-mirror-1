.. pydataportability.discovery documentation master file, created by sphinx-quickstart on Fri Oct  9 12:59:36 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================
:mod:`pydataportability.discovery`
==================================

:mod:`pydataportability.discovery` is combining several other pydataportability
components in order to provide URI based discovery of resource description
documents.

In plain words that means that you give it a URI of a resource (e.g. a web
URL) and it will try to find a document containing metadata for it which can
either be in :term:`XRDS-Simple` or :term:`XRD` format.

.. note:: :term:`XRDS-Simple` is going to be replaced by the upcoming 
    :term:`XRD` specification. The latter has no final release at the point
    of this writing which means that the API is likely going to change before
    the final release of this component.
    

Contents:

.. toctree::
   :maxdepth: 2
   
   installation
   usage
   innerworkings
   extending
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`

