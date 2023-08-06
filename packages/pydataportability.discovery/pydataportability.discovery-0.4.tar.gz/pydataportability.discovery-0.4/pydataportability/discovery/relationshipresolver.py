import copy
from pydataportability.model.resource.models import TemplateError
from urlparse import urlparse


class GenericResolver(object):
    """the generic resolver works on ``describedby`` links and it is
    capable of resolving URI templates containing ``%uri`` placeholders
    as well as those passed in via keyword arguments."""
    
    def update_kws(self, kws, uri):
        """a hook for being overwritten in subclasses. ``kws`` is a copy of the
        ``**kws`` passed in from the application and ``uri`` is the URI we are
        trying to find the :term:`Resource Description` for. You can update
        the ``kws`` dictionary as you see fit."""
    
    def resolve(self, link, uri, **kws):
        """return the first resolved URI template inside the ``link`` object which
        can be resolved. ``uri`` is the original URI passed into the discovery process
        and ``kws`` is an optional list of arguments passed in by the application."""
        
        kws = copy.copy(kws)
        kws['uri'] = uri
        self.update_kws(kws, uri) # hook for changing the kws dict in subclasses
        for tmpl in link.templates:
            try:
                resolved_uri = tmpl(**kws)
            except TemplateError, e:
                # resolving it failed, try the next one
                continue
            else:
                return resolved_uri
        # resolving it failed, return None (other handlers might still work)
        return None
        

class WebfingerResolver(GenericResolver):
    """a IRelationshipResolver for resolving URI
    templates based on ``http://webfinger.info/rel/service`` relationships"""
    
    def update_kws(self, kws, uri):
        """add the ``%id`` parameter from the URI"""
        
        # we are only interested in the address so let's parse it out
        scheme, foo, acct, foo, foo, foo = urlparse(uri) 
        kws['id'] = acct # this is the key function here
