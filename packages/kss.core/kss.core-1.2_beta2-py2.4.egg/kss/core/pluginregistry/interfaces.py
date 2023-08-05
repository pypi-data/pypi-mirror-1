from zope.interface import Interface

class IAzaxPlugin(Interface):
    '''Base for azax plugins
    
    this represents an entity implemented in a javascript file
    '''

class ICommand(IAzaxPlugin):
    '''Command plugin'''

class IAction(IAzaxPlugin):
    '''Action plugin'''

class IEventType(IAzaxPlugin):
    '''Event type plugin'''

class ISelectorType(IAzaxPlugin):
    '''Selector type plugin'''

class ICommandSet(Interface):
    '''Command set plugin'''

class IParamProvider(IAzaxPlugin):
    '''Parameter provider plugin'''
