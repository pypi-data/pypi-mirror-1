from pydataportability.discovery.acctservice import AcctSchemeHandler, URIMalformedError

from py.test import raises

def test_acct_scheme_basic():
    ash = AcctSchemeHandler()
    assert ash.extract_host("acct:mrtopf@example.com") == ("example.com", 80, "http")
    
def test_acct_scheme_invalid_http_uri():
    ash = AcctSchemeHandler()    
    raises(URIMalformedError, lambda : ash.extract_host("http://mrtopf.example.com"))
    
def test_acct_scheme_invalid_acct_uri():
    ash = AcctSchemeHandler()    
    raises(URIMalformedError, lambda : ash.extract_host("acct:mrtopf"))
    
def test_acct_scheme_empty_uri():
    ash = AcctSchemeHandler()    
    raises(URIMalformedError, lambda : ash.extract_host("acct:"))

def test_acct_scheme_no_domain():
    ash = AcctSchemeHandler()    
    raises(URIMalformedError, lambda : ash.extract_host("acct:mrtopf@"))


# TODO: What about mrtopf@mrtopf@example.com? 