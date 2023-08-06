from urlparse import urlparse

from zope.interface import implements
from zope.component import getUtility, queryUtility

from pydataportability.xrd import parse_xrd

from interfaces import IHostMetaSchemeHandler, IRelationshipResolver
from discovery import URIMalformedError, DiscoveryError
from network import retrieve_url

class HostMetaDiscoveryService(object):
    """a discovery service which works on the host meta document"""
        
    def discover(self, uri, rels=['describedby'], protocol="http"):
        """try to obtain the host meta document from the given ``uri``. For this to work
        the URI is first split into it's components and then the host part is used to obtain the
        host-meta document. This method will then compute the URL of the actual resource description,
        retrieve it and return the resource description data.
        """
        
        scheme, netloc, path, params, query, fragment = urlparse(uri)
        
        # retrieve the scheme handler for the given scheme
        scheme_handler = queryUtility(IHostMetaSchemeHandler, name=scheme, default=None)
        if scheme_handler is None:
            scheme_handler = getUtility(IHostMetaSchemeHandler) # get the default one
        
        host, port, protocol = scheme_handler.extract_host(uri, protocol)
        
        # now we retrieve the host meta document by the given protocol
        if protocol=="http":
            hm_uri = "http://%s:%s/.well-known/host-meta" %(host,port)
            fp = retrieve_url(hm_uri)
            resource = parse_xrd(fp)
            fp.close()
        else:
            raise DiscoveryError(uri, u"protocol %s not supported" %protocol)

        # now that we have the host meta XRD we need to check for the rel
        # we are looking for (default is "describedby") and compute the URI to the
        # XRD file of the actual resource

        # TODO: check for matching <Host> tag
        # TODO: filter() makes an AND which is maybe not what we want.. how 
        # can this be modelled better (we might want "webfinger" or "describedby")
        links = resource.links.filter(rels=rels)
        
        # PROBLEM: res now has a URITemplate with an %id parameter which is defined
        # for webfinger but not for described by.
        # this means that we now need to lookup a handler for this particular rel
        
        # we simply use the first hit and return it
        # TODO: maybe check priorities here, too (or maybe in filter())
        
        rd_uri = None # resource description URI
        for link in links:
            # in case we find a URI without a template simply return it
            if len(link.uris)!=0:
                rd_uri = link.uris[0]
                break
            for rel in link.rels:
                # we have templates instead so we need to find a handler
                # which can handle the set of attributes
                rel_handler = queryUtility(IRelationshipResolver, name=rel, default=None)
                if rel_handler is None:
                    continue
                rd_uri = rel_handler.resolve(link,uri) # feed in all we have
                # TODO: maybe provide a **kw way of providing more information
                # from the application to this handler.
                if rd_uri is not None: 
                    break
            if rd_uri is not None:
                break
        if rd_uri is None:
            raise DiscoveryError(uri, u"no valid URI or URITemplate found in host meta")

        # now we can simple return the resulting XRD file
        fp = retrieve_url(rd_uri)
        resource = parse_xrd(fp)
        fp.close()
        return resource
        
            
        
