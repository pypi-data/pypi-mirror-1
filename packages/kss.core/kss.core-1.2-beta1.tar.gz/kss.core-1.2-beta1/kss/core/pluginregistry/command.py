
from plugin import AzaxPlugin
from interfaces import ICommand
from plugin import AzaxPluginError
import zope.component as capi
from zope.interface import implements

def checkRegisteredCommand_old(name):
    'Check if it is a registered command.'
    try:
        command = capi.getUtility(ICommand, name)
    except capi.ComponentLookupError:
        raise AzaxPluginError, '"%s" is not a registered kss command' % (name, )

class Command(AzaxPlugin):
    '''The command plugin

    '''

    implements(ICommand)

    def __init__(self, name, jsfile):
        AzaxPlugin.__init__(self, name, jsfile)
