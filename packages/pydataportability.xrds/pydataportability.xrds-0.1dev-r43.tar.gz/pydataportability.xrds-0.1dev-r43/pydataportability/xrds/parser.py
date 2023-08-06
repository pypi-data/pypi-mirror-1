from elementtree.ElementTree import parse

class URI(object):
    """an URI representation with priority"""

    def __init__(self, uri, method, prio):
        self.uri = uri
        self.prio = prio
        self.method = method
        


class Service(object):
    """a service definition"""
    def __init__(self, typ, uris=[], priority=0, localid=""):
        self.uris = uris
        self.priority = priority
        self.type = typ
        self.localid = localid
        

class XRDSParser(object):
    """parse an xrds document"""
    
    def __init__(self,fp):
        tree = parse(fp)
        elem = tree.getroot()
        services = elem.findall("*/{xri://$XRD*($v*2.0)}Service")
        self._services=[]

        for service in services:
            typ = service.find("{xri://$XRD*($v*2.0)}Type").text
            uris = service.findall("{xri://$XRD*($v*2.0)}URI")
            localid = service.find("{xri://$XRD*($v*2.0)}LocalID")
            prio = service.attrib.get('priority',0)
            uri_objects = []
            for uri in uris:
                method = uri.attrib.get("{http://xrds-simple.net/core/1.0}httpMethod","GET")
                prio = uri.attrib.get("{http://xrds-simple.net/core/1.0}priority","0")
                u = URI(uri.text,method,prio)
                uri_objects.append(u)
            s = Service(typ, uri_objects, prio, localid)
            self._services.append(s)


    @property
    def services(self):
        """return the services found"""
        return self._services
        

if __name__=="__main__":        
    fp = open("xrds.xml","r")
    p = XRDSParser(fp)
    fp.close()
    for s in p.services:
        print "Type:",s.type
        print "Prio:",s.priority
        print "LocalID:",s.localid        
        for uri in s.uris:
            print "  ",uri.uri
            
        print 
