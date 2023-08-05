
from plugin import AzaxPlugin
from interfaces import IParamProvider
import zope.component as capi
from zope.interface import implements

class ParamProvider(AzaxPlugin):
    '''The parameter provider plugin
    '''

    implements(IParamProvider)

    def __init__(self, name, jsfile):
        AzaxPlugin.__init__(self, name, jsfile)
