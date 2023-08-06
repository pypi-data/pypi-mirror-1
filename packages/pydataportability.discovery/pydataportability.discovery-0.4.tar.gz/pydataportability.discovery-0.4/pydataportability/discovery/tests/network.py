import urllib
import os

from pydataportability.discovery.interfaces import IURLRetriever


class DummyURLRetriever(object):
    """return a dummy host meta file"""
    
    def retrieve(self, url):
        if url=="http://example.com:80/.well-known/host-meta":
            # the host-meta file for webfinger like retrieval
            filename = os.path.abspath(os.path.dirname(__file__))+"/host-meta.example"
            fp = open(filename)
            return fp
        elif url=="http://webfinger.example.com/?id=mrtopf@example.com":
            # the actual webfinger XRD file
            filename = os.path.abspath(os.path.dirname(__file__))+"/webfinger.xrd"
            fp = open(filename)
            return fp
            
