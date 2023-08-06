from zope.interface import Interface

class IDiscoveryService(Interface):
    """describes a generic discovery service for obtaining an instance of
    ``pydataportability.model.resource.models.Resource`` (or in general 
    ``pydataportability.model.resource.interfaces.IResource``)"""
    
    def discover(uri):
        """perform resource description discovery on the resource identified by
        the given ``uri`` parameter and return an object which implements
        ``pydataportability.model.resource.interfaces.IResource``"""

### the types of LRDD discovery
# 

class IHostMetaDiscoveryService(IDiscoveryService):
    """perform host meta discovery for a given host"""
    
        
        
class IHostMetaSchemeHandler(Interface):
    """a component for extracting a host from a URI with a given schema"""

    def extract_host():
        """return the host on which to look for the host meta document"""


class IRelationshipResolver(Interface):
    """a component which is able to resolve a URI template based on a
    given relationship type"""
    
    def resolve(link, uri):
        """``link`` is the :mod:`pydataportability.model.resource.interface.IResourceLink`
            which contains the URI template in question. ``uri`` is the
            URI of the resource we want to find the :term:`Resource Description`
            for. This method returns the rendered URI template. If the URI
            template couldn't get rendered (e.g. because a parameter is unknown)
            or there is no URI template in the link then this method must return
            None."""
            
            
class IURLRetriever(Interface):
    """component for retrieving a URL. This is right now mostly used for testing purposes
    so that we can replace the call to ``urlopen()`` with our own method for returning
    dummy data"""
    
    def retrieve(url):
        """retrieve the document at ``url`` via HTTP and return a file like object.
        """