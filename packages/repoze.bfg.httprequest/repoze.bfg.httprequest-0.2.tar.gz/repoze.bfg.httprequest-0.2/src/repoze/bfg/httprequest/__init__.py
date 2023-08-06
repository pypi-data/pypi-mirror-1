import sys
import imp

module_name = 'repozehttprequestinterfaces'
interfaces = sys.modules[module_name] = imp.new_module(module_name)

global_registry = {}
class_registry = {}

class RequestInterfacesImporter(object):
    """This module importer class dynamically restores adapted
    interfaces."""
    
    def find_module(self, fullname, path=None):
        if fullname == module_name:
            for key, iface in class_registry.items():
                #ifaces = adapter.get_ifaces_for_key(key)
                setattr(interfaces, key, iface)
            return self
        
    def load_module(self, fullname):
        sys.modules[fullname] = interfaces
        return interfaces

sys.meta_path.append(RequestInterfacesImporter())

import repozehttprequestinterfaces
import adapter
