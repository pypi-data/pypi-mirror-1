from urlparse import urlparse
from urllib2 import urlopen

from zope.interface import implements
from zope.component import getUtility

from pydataportability.xrd import parse_xrd

from interfaces import IHostMetaSchemeHandler
from discovery import URIMalformedError, ResourceDescriptionNotFound

class AcctSchemeHandler(object):
    """a discovery service which works on ``acct`` URI schemes"""
    
    implements(IHostMetaSchemeHandler)
    
    def extract_host(self, uri, protocol="http"):
        """here we need to extract the host from the URI"""
        
        scheme, foo, acct, foo, foo, foo = urlparse(uri) # we are only interested in the address

        try:
            user, host = acct.split("@")
        except ValueError:
            # if we get more or less than 2 parts
            raise URIMalformedError(uri)

        if host.strip()=="":
            raise URIMalformedError(uri, "host part is empty")
        return host, 80, protocol
        
        
        
        
        
        
        
        
    
    
