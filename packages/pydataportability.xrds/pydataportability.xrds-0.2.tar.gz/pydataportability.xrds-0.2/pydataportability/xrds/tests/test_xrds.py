from pydataportability.xrds.parser import XRDSParser
from datetime import datetime

def test_xrds_lower_ns_amount(fp1):
    p = XRDSParser(fp1)
    assert len(p.services) == 5
    
def test_xrds_service_basics(fp1):
    p = XRDSParser(fp1)
    s = p.services[0]
    assert s.type == "http://specs.openid.net/auth/2.0/signon"
    assert s.priority == 0
    assert len(s.localids) == 3
    assert len(s.uris) == 1
    
def test_xrds_localids(fp1):
    p = XRDSParser(fp1)
    s = p.services[0]
    lis = s.localids
    assert lis[0].priority == 10
    assert lis[1].priority == 20
    assert lis[2].priority == None
    assert lis[0].localid == "http://mrtopf1.myopenid.com/"
    assert lis[1].localid == "http://mrtopf2.myopenid.com/"
    assert lis[2].localid == "http://mrtopf3.myopenid.com/"    
    
def test_xrds_uris(fp1):
    p = XRDSParser(fp1)
    s = p.services[1]
    uris = s.uris
    assert uris[0].priority == 3
    assert uris[1].priority == 1
    assert uris[2].priority == None
    assert uris[0].uri == "http://www.myopenid.com/server3"
    assert uris[1].uri == "http://www.myopenid.com/server1"
    assert uris[2].uri == "http://www.myopenid.com/servernull"    
    assert uris[0].method == "GET"
    assert uris[1].method == "POST"
    assert uris[2].method == "DELETE"    
    
    
def test_xrds_service_prios(fp1):
    p = XRDSParser(fp1)
    assert p.services[0].priority == 0
    assert p.services[1].priority == 1
    assert p.services[2].priority == 2
    assert p.services[3].priority == 0
    assert p.services[4].priority == 0


def test_xrds_upper_ns_amount(fp2):
    """check if XRD or xrd works both as namespaces"""
    p = XRDSParser(fp2)
    assert len(p.services) == 5
