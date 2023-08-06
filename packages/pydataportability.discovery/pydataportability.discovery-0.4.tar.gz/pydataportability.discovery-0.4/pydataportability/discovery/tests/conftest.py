import os
import py
import pydataportability.discovery
from zope.component import getSiteManager
import zope.configuration.xmlconfig


# functions for configuring the right components for each test

CONFIGS = {
    'pydataportability.discovery.tests.test_hostmeta' : ('tests/hm_configure1.zcml', pydataportability.discovery),
}
DEFAULT_CONFIGURE = ('tests/configure.zcml', pydataportability.discovery)

CONFIGURED_CLASSES = []


def cleanup():
    getSiteManager.reset()
    
    

def setup_configure(item, configs=CONFIGS, default=DEFAULT_CONFIGURE):
    """setup the right configuration by inspecting the item which is going to be tested.
    We first check if it's a function collected by py.test (also methods are collected that way).
    Then we try to find the class it belongs to. In case it's a function it will result in None but
    otherwise it will be the TestClass the method belongs to. We use getparent() for that
    Then we check a local CONFIGURES mapping to find out which file from which package needs to be
    read by the ZCML configuration machinery.

    We could also inspect modules by using item.getparent(py.test.collect.Module)
    """
    name = str(item.obj)
    if isinstance(item, py.test.collect.Function):
        klass = item.getparent(py.test.collect.Class)
        if klass is None:
            filename, pkg = default
        else:
            name = str(klass.obj)
            print "***",name
            filename, pkg = configs.get(name, default)
    else:
        filename, pkg = default
    if name in CONFIGURED_CLASSES:
        # already configured
        return


    # now our test related configs
    zope.configuration.xmlconfig.file(filename, package=pkg)
    CONFIGURED_CLASSES.append(name)

def teardown(item):
    name = str(item.obj)
    if isinstance(item, py.test.collect.Function):
        klass = item.getparent(py.test.collect.Class)
    if klass is not None:
        name = str(klass.obj)
    if name in CONFIGURED_CLASSES:
        cleanup()
        CONFIGURED_CLASSES.remove(name)


def pytest_runtest_setup(item):
    """this is run whenever a test needs to be setup"""
    setup_configure(item)

def npytest_runtest_teardown(item):
    """at teardown time we remove any configuration we did for an item before, mainly
    removing the ZCA configuration. You can also create your own ``pytest_runtest_teardown()``
    method in your tests and call ``teardown(item)`` from there."""
    teardown(item)

    
###
### fixture for relationship resolver
###

from pydataportability.model.resource import ResourceLink, URITemplate

class RelationshipResolverFixture:
    
    webfinger_rel = "http://webfinger.info/rel/service"
    webfinger_uri = "acct:mrtopf@example.com"
    webfinger_link = ResourceLink(rels = ['http://webfinger.info/rel/service'],
                                  templates = ['http://example.com/resolve?id={%id}'])
    webfinger_resolved_uri = "http://example.com/resolve?id=mrtopf@example.com"

    describedby_rel = "describedby"
    describedby_uri = "http://example.com"
    describedby_link = ResourceLink(rels = ['describedby'],
                                  templates = ['http://example.com/resolve?uri={%uri}'])
    describedby_resolved_uri = "http://example.com/resolve?uri=http://example.com"
        

def pytest_funcarg__resolver_fixture(request):
    return RelationshipResolverFixture()
    
    
###
### fixture for host meta based discovery
###

class HostMetaFixture:
    """host meta"""
    
def pytest_funcarg__hostmeta_fixture(request):
    return HostMetaFixture()