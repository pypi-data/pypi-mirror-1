
from plugin import AzaxPlugin
from interfaces import IEventType
from zope.interface import implements

class EventType(AzaxPlugin):
    '''The event type plugin

    '''

    implements(IEventType)

    def __init__(self, name, jsfile):
        AzaxPlugin.__init__(self, name, jsfile)

