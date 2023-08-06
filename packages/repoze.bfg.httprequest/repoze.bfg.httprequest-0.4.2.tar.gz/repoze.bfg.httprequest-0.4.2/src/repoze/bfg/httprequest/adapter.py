from zope import interface
from zope import component
from zope.interface.interface import adapter_hooks

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import INewRequest

from repoze.bfg.httprequest import global_registry, class_registry

import urllib
import operator

name_getter = operator.attrgetter('__name__')

class Checker(object):

    def __init__(self, name, token):
        self.name = name
        self.normalized_value = str(token).lower()

    def __call__(self, other):
        return self.normalized_value in other

    def __repr__(self):
        return "<Checker for %s=%s>" % (self.name, self.normalized_value)

@interface.implementer(IRequest)
def request_factory(environ):
    import repoze.bfg.httprequest
    interfaces = repoze.bfg.httprequest.interfaces

    class Interface(type(interface.Interface)):
        def __repr__(self):
            return '<IHTTPRequest %s>' % urllib.urlencode(environ)

    ifaces = tuple(get_matching_interfaces(environ))
    IHTTPRequest = Interface("IHTTPRequest", (IRequest,) + ifaces)
    IHTTPRequest.environ = environ

    ifaces = []
    for name, token in environ.items():
        # if token is a string, then use a standard comparison method
        # which checks if the request has a value which appears in the
        # lowercased match string
        if isinstance(token, (str, unicode)):
            method = Checker(name, token)
        # else, assume token is a truth function
        else:
            method = token

        key = name.lower(), method
        iface = global_registry.get(key)
        if iface is None:
            class IRequestMarker(interface.Interface):
                pass
            IRequestMarker.__module__ = interfaces
            IRequestMarker.__name__ = (
                "I%s%d" % (name, id(token))).encode('hex_codec')
            iface = global_registry[key] = IRequestMarker

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

# add adapter hook to adapt dicts to the ``IRequest`` interface
def adapt_dict_to_request(iface, ob):
    if iface.isOrExtends(IRequest):
        return request_factory(ob)
    
adapter_hooks.append(adapt_dict_to_request)

@component.adapter(INewRequest)
def new_request_handler(new_request_event):
    request = new_request_event.request

    for iface in get_matching_interfaces(request.environ):
        interface.alsoProvides(request, iface)
        
def get_matching_interfaces(environ):
    ifaces = []

    for name1, value1 in environ.items():
        name1 = name1.lower()
        value1 = str(value1).lower()
        for name2, value2 in global_registry:
            if name1 != name2:
                continue

            if value2(value1):
                iface = global_registry[name2, value2]
                ifaces.append(iface)

    # sort interfaces by name for consistent ordering
    ifaces.sort(key=name_getter)

    for n in range(1, len(ifaces)+1):
        for _ifaces in xuniqueCombinations(ifaces, n):
            key = get_key_for_ifaces(sorted(_ifaces))
            iface = class_registry.get(key)
            if iface is not None:
                yield iface

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
