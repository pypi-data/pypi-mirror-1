from zope.interface import implements
import zope.component as capi

from plugin import AzaxPluginError
from plugin import registerPlugin
from interfaces import ICommandSet

def getRegisteredCommandSet(name):
    'Get the command set'
    try:
        commandset = capi.getUtility(ICommandSet, name)
    except capi.ComponentLookupError:
        raise AzaxPluginError, '"%s" is not a registered kss command set' % (name, )
    return commandset

class CommandSet(object):
    '''The command set plugin

    registers the command adapter interface
    (like IKssCoreCommands), this makes possible
    to look them up by name instead of by interface
    '''

    implements(ICommandSet)

    def __init__(self, name, provides):
        self.name = name
        self.provides = provides

def registerAndAllowCommandSet(class_, name, provides, *arg, **kw):
    registerPlugin(CommandSet, ICommandSet, name, provides, *arg, **kw)
    try:
        import Products.Five
    except ImportError:
        pass
    else:
        # Allow TTW to use commandsets
        from AccessControl import allow_class
        allow_class(class_)
    
