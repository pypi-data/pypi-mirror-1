from pydataportability.discovery import discover
from zope.component import getUtility, queryUtility
from pydataportability.discovery.interfaces import IHostMetaSchemeHandler, IDiscoveryService

def test_acct_uri_discovery():
    """check if a host meta file can be retrieved from a URL
    """
    uri = "mrtopf@example.com"
    scheme_handler = queryUtility(IHostMetaSchemeHandler, name="acct")
    assert scheme_handler is not None
    
    host, port, protocol = scheme_handler.extract_host(uri, "http")
    assert host == "example.com"
    assert port == 80
    assert protocol == "http"
    
    


def test_hostmeta_discovery(hostmeta_fixture):
    uri = "acct:mrtopf@example.com"
    service = getUtility(IDiscoveryService, name="hostmeta")
    result = service.discover(uri, rels=['http://webfinger.info/rel/service'])
    assert result.subject == uri
    assert len(result.links)==1
    link = result.links[0]
    assert link.rels == ['http://portablecontacts.net/spec/1.0']
    assert link.uris == ['http://www-opensocial.example.com/api/people/']

    
    
