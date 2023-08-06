try:
    from elementtree.ElementTree import parse
except ImportError:
    from xml.etree.ElementTree import parse
    
from UserList import UserList

class URI(object):
    """an URI representation with priority"""

    def __init__(self, uri, method, priority=None):
        self.uri = uri
        self.priority = priority
        self.method = method
        
    def __repr__(self):
        return """<URI '%s' with priotity %s and method '%s'>""" %(self.uri, self.priority, self.method)


class LocalID(object):
    """a localid representation with a priority"""

    def __init__(self, localid, priority=None):
        self.localid = localid
        self.priority = priority
        
    def __repr__(self):
        return """<LocalID '%s' with priotity %s>""" %(self.localid, self.priority)


class Service(object):
    """a service definition"""
    def __init__(self, type_, uris=[], priority=None, localids=[]):
        self.uris = uris
        self.priority = priority
        self.type = type_
        self.localids = localids


class ServiceRegistry(UserList):
    """a list of services"""

    def get_service_by_type(self, type_, prefix=False):
        """return all services which match a given type

        If prefix is True then only the common prefix will be searched.
        That way you might be able to search for a type without a version info.
        
        """
        if prefix:
            return [service for service in self if service.type == type_]
        else:
            return [service for service in self if service.type.startswith(type_)]

def compute_prio(prio):
    """check if ``null`` is given as priority and return None instead. an integer otherwise"""
    if prio=="null":
        return None
    return int(prio)

class XRDSParser(object):
    """parse an xrds document"""

    def __init__(self,fp):
        tree = parse(fp)
        elem = tree.getroot()
        self._services=ServiceRegistry()

        for ns in ("xri://$xrd*($v*2.0)", "xri://$XRD*($v*2.0)"):
            services = elem.findall("*/{%s}Service" % ns)
            for service in services:
                typ = service.find("{%s}Type" % ns).text
                uris = service.findall("{%s}URI" % ns)
                service_prio = compute_prio(service.attrib.get('priority','0'))

                li_elements = service.findall("{%s}LocalID" % ns)
                localids = []
                for li in li_elements:
                    li_prio = compute_prio(li.attrib.get("priority","0"))
                    localids.append(LocalID(li.text, li_prio))

                uri_objects = []
                for uri in uris:
                    method = uri.attrib.get("{http://xrds-simple.net/core/1.0}httpMethod","GET")
                    prio = compute_prio(uri.attrib.get("priority","0"))
                    u = URI(uri.text,method,prio)
                    uri_objects.append(u)
                s = Service(typ, uri_objects, service_prio, localids)
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
