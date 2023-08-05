
from plugin import AzaxPlugin
from interfaces import ISelectorType
import zope.component as capi
from zope.interface import implements

def checkRegisteredSelector(name):
    'Check if it is a registered selector.'
    try:
        command = capi.getUtility(ISelectorType, name)
    except capi.ComponentLookupError:
        raise AzaxPluginError, '"%s" is not a registered kss selector' % (name, )

class SelectorType(AzaxPlugin):
    '''The selectortype plugin

    '''

    implements(ISelectorType)

    def __init__(self, name, jsfile):
        AzaxPlugin.__init__(self, name, jsfile)
