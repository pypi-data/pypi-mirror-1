from zope import interface
from zope import component

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import INewRequest

from repoze.bfg.httprequest import global_registry, class_registry

import urllib
import operator
import repoze.bfg.httprequest

interfaces = repoze.bfg.httprequest.interfaces

@interface.implementer(IRequest)
def request_factory(environ):
    class Interface(type(interface.Interface)):
        def __repr__(self):
            return '<IHTTPRequest %s>' % urllib.urlencode(environ)

    IHTTPRequest = Interface("IHTTPRequest", (IRequest,))
        
    ifaces = []
    
    for name, value in environ.items():
        key = (name, value)
        iface = global_registry.get(key)
        if iface is None:
            class IMarker(interface.Interface):
                pass
            IMarker.__module__ = interfaces
            IMarker.__name__ = "I"+(name+value).encode('hex_codec')
            iface = global_registry[key] = IMarker

        ifaces.append(iface)
        interface.alsoProvides(IHTTPRequest, iface)

    ifaces.sort(key=operator.attrgetter('__name__'))
    key = get_key_for_ifaces(ifaces)
    iface = class_registry.get(key)
    if iface is None:
        iface = class_registry[key] = IHTTPRequest
    
        # tuple(sorted(ifaces))
        IHTTPRequest.__module__ = repoze.bfg.httprequest.module_name
        IHTTPRequest.__name__ = key
        setattr(interfaces, key, IHTTPRequest)

    return iface

# we make this adapter available at module import time
component.provideAdapter(request_factory, (dict,))

@component.adapter(INewRequest)
def new_request_handler(new_request_event):
    ifaces = []
    request = new_request_event.request
    for name1, value1 in request.environ.items():
        for (name2, value2), iface in global_registry.items():
            if name1 == name2 and value2 in value1:
                ifaces.append(iface)

    ifaces.sort(key=operator.attrgetter('__name__'))

    for n in range(1, len(ifaces)+1):
        for _ifaces in xuniqueCombinations(ifaces, n):
            key = get_key_for_ifaces(sorted(_ifaces))
            iface = class_registry.get(key)
            if iface is not None:
                interface.alsoProvides(request, iface)

def xuniqueCombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xuniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc            
        
def get_key_for_ifaces(ifaces):
    return ",".join(iface.__name__ for iface in ifaces)

def get_ifaces_for_key(key):
    return tuple(global_registry[name] for name in key.split(','))
