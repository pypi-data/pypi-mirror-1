from pydataportability.discovery import discover
from zope.component import getUtility, queryUtility
from pydataportability.discovery.interfaces import IRelationshipResolver

from pydataportability.model.resource.models import ResourceLink


def test_webfinger_resolver_base(resolver_fixture):
    """check if the webfinger resolver is able to resolve webfinger URI
    """
    rf = resolver_fixture
    rel_handler = getUtility(IRelationshipResolver, 
            name=rf.webfinger_rel)
    rd_uri = rel_handler.resolve(rf.webfinger_link,rf.webfinger_uri) # feed in all we have

    assert rd_uri == rf.webfinger_resolved_uri
    
    
def test_describedby_resolver_base(resolver_fixture):
    """check if the describedby resolver is able to resolve webfinger URI
    """
    rf = resolver_fixture
    rel_handler = getUtility(IRelationshipResolver, 
            name='describedby')
    rd_uri = rel_handler.resolve(rf.describedby_link,rf.describedby_uri) # feed in all we have

    assert rd_uri == rf.describedby_resolved_uri

