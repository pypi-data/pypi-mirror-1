
from interfaces import IAzaxPlugin
import zope.component as capi
from zope.interface import implements

class AzaxPluginError(Exception):
    pass
 
def registerPlugin(cls, interface, name, *arg, **kw):
    'Convenience method to help registration'
    plugin = cls(name, *arg, **kw)
    # check if it's registered: do not allow registration for the second name
    try:
        capi.getUtility(interface, name=name)
    except capi.ComponentLookupError:
        pass
    else:
        raise AzaxPluginError, 'Duplicate registration attempt for plugin "%s" of type %s' % (plugin.name, interface)
    # provide the utility.
    capi.provideUtility(plugin, interface, name=name)

class AzaxPlugin(object):
    'The base plugin class'

    implements(IAzaxPlugin)

    def __init__(self, name, jsfile):
        self.name = name
        self.jsfile = jsfile
