import urllib

from zope.component import getUtility

from interfaces import IURLRetriever

def retrieve_url(url):
    """helper method for using the configured ``IURLRetriever`` component to
    retrieve the document at the given ``url``. Use this instead of using the ZCA
    methods directly."""
    
    handler = getUtility(IURLRetriever)
    return handler.retrieve(url)

class URLRetriever(object):
    """helper component for retrieving the document for a URL
    
    TODO: Maybe this should be a separate component in pydataportability at some point
    TODO: What about asynchronous retrieving? Read: support for tornado or twisted?
    """
    
    def retrieve(self, url):
        """retrieve the given URL"""
        fp = urllib.urlopen(url)
        return fp
