from urlparse import urlparse

from zope.component import queryUtility

from pydataportability.xrd import parse_xrd

from interfaces import IDiscoveryService

class DiscoveryError(Exception):
    """generic class for an exception raised during discovery. It takes the ``uri`` on which
    discovery was tried and an optional ``msg`` parameter explaining the error details as 
    parameters"""
    
    msg = u"generic discovery error"
    
    def __init__(self, uri, msg = None):
        """initialize the error instance"""
        self.uri = uri
        if msg is not None:
            self.msg = msg
        
    def __repr__(self):
        return """Discovery Error on URI '%s': %s""" %(self.uri, self.msg)
    
    __str__ = __repr__
    
class SchemeNotSupportedError(DiscoveryError):
    """exception which is being raised if no discovery component for handling the
    scheme of the URI is being found."""
    
    msg = u"URI scheme used is not supported."

class URIMalformedError(DiscoveryError):
    """exception which is being raised if the URI is not formatted as it is supposed to be."""

    msg = u"the given URI is malformed."
    
class ResourceDescriptionNotFound(DiscoveryError):
    """raised if the resource description couldn't be found"""
    
    msg = u"resource description couldn't be found"

def discover(resource_uri, methods=['linkheader','linkdocument','hostmeta'],
                       rels=['describedby']):
    """do LRDD discovery on the given ``uri`` and return an instance of 
    ``pydataportability.model.resource.model.ResourceSet``. This is not the final metadata
    descriptor for the resource but simply a list of links which contain potential metadata
    descriptors. The application then has to select the appropriate one and retrieve the actual
    resource description.

    The optional ``methods`` parameter defines which utilities for retrieving the resource descriptions 
    are used in which sequence. These will lookup components with type ``IDiscoveryService`` and the
    given name.
    
    The ``rels`` parameter is a list of values of the ``rel``-Attribute of links we regard as valid 
    relationship types for any methods. Default is ``describedby`` as defined in the LRDD specification.
    """
    
    result = None
    for method in methods:
        service = queryUtility(IDiscoveryService, method)
        if service is None:
            continue
        result = service.discover(resource_uri, rels)
        if result is not None:
            return result
    # TODO: should the discovery service really return the XRD? Or maybe just the link
    # to it instead? A case against it would be XRDS-Simple support where the plugin
    # could directly resolve the XRDS file. OTOH it could also return the media_types found
    # and in case it's an XRD file we do XRD discovery and in case of XRDS we do this.
    # then again the question is how relevant XRDS-Simple will be and if we always
    # get a media type back. But the latter problem stays a problem anyways.
    return None # no result found
    
    # TODO: discuss if an exception is better to raise:
    raise ResourceDescriptionNotFound(uri, msg="no provided discovery service could retrieve" 
                    "the resource description. Methods tried: %s" %methods)



import sys
import zope.configuration.xmlconfig
import pydataportability.discovery

def main():
    # set up all components
    zope.configuration.xmlconfig.file('configure.zcml', package=pydataportability.discovery)
    
    # now perform the discovery
    uri = sys.argv[1]
    
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
        
def webfinger():
    """do discovery for webfinger enabled URIs"""
    
    
    zope.configuration.xmlconfig.file('configure.zcml', package=pydataportability.discovery)
    uri = sys.argv[1]
    
    # make sure we have an acct-URI
    if not uri.startswith("acct:"):
        uri = "acct:"+uri
        
    resource = discover(uri, ['hostmeta'], rels=["http://webfinger.info/rel/service"])
    
    for link in resource.links:
        print "Rels: ", link.rels
        print "URIs:", link.uris
        print "Media Types:", link.media_types
        print "Prio:", link.priority
        print "Templates:", link.templates
        print
    
    
        
        
