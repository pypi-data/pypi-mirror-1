
from zope.component.zcml import adapter
from interfaces import IEventType, ISelectorType, IAction, IParamProvider
from event_type import EventType
from action import Action
from selector_type import SelectorType
from commandset import registerAndAllowCommandSet
from pprovider import ParamProvider
from plugin import registerPlugin

#class AzaxConfigurationError(Exception):
#    pass

def registerEventType(_context, name, jsfile=None):
    'Directive that registers an event type' 
    
    # check to see if the file exists
    if jsfile is not None:
        file(jsfile, 'rb').close()

    _context.action(
        discriminator = ('registerKssEventType', name, jsfile),
        callable = registerPlugin,
        args = (EventType, IEventType, name, jsfile),
        )
 
def registerAction(_context, name, jsfile=None, command_factory='none',
        params_mandatory=[], params_optional=[], deprecated=None):
    'Directive that registers an action.' 
    
    # check to see if the file exists
    if jsfile is not None:
        file(jsfile, 'rb').close()

    _context.action(
        discriminator = ('registerKssAction', name, jsfile),
        callable = registerPlugin,
        args = (Action, IAction, name, jsfile, command_factory, params_mandatory, params_optional, deprecated),
        )

def registerSelectorType(_context, name, jsfile=None):
    'Directive that registers a selector type' 
    
    # check to see if the file exists
    if jsfile is not None:
        file(jsfile, 'rb').close()

    _context.action(
        discriminator = ('registerKssSelectorType', name, jsfile),
        callable = registerPlugin,
        args = (SelectorType, ISelectorType, name, jsfile),
        )

def registerCommandSet(_context, for_, class_, name, provides):
    'Directive that registers a command set' 
    
    adapter(_context, [class_], provides, [for_])
    _context.action(
        discriminator = ('registerKssCommandSet', name),
        callable = registerAndAllowCommandSet,
        args = (class_, name, provides),
        )

def registerParamProvider(_context, name, jsfile=None):
    'Directive that registers a parameter provider' 
    
    # check to see if the file exists
    if jsfile is not None:
        file(jsfile, 'rb').close()

    _context.action(
        discriminator = ('registerKssParamProvider', name),
        callable = registerPlugin,
        args = (ParamProvider, IParamProvider, name, jsfile),
        )
