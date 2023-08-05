
from plugin import AzaxPlugin, AzaxPluginError
from interfaces import IAction
from zope.interface import implements
import zope.component as capi

def checkRegisteredCommand(name):
    'Check if it is a registered command.'
    try:
        command = capi.getUtility(IAction, name)
    except capi.ComponentLookupError:
        raise AzaxPluginError, '"%s" is not a registered kss command' % (name, )
    # check if the action has a valid command factory
    if command.command_factory == 'none':
        raise AzaxPluginError, '"%s" kss command has missing command_factory' % (name, )
    # issue deprecation warning, if necessary
    command.check_deprecation()

class Action(AzaxPlugin):
    '''The action plugin

    '''

    implements(IAction)

    def __init__(self, name, jsfile, command_factory, 
            params_mandatory, params_optional, deprecated):
        AzaxPlugin.__init__(self, name, jsfile)
        self.command_factory = command_factory
        self.params_mandatory = params_mandatory
        self.params_optional = params_optional
        self.deprecated = deprecated

    def check_deprecation(self):
        if self.deprecated:
            import warnings, textwrap
            warnings.warn(textwrap.dedent('''\
            The usage of the kss command "%s" is deprecated,
            %s''' % (self.name, self.deprecated)), DeprecationWarning, 2)
