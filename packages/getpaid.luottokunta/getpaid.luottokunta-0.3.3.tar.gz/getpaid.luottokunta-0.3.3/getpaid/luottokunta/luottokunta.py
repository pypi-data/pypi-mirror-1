from zope.interface import implements
from zope.component import adapts
#from Products.CMFCore.interfaces import ISiteRoot
from getpaid.core.interfaces import IStore
from getpaid.core.interfaces import keys
from getpaid.luottokunta.interfaces import ILuottokuntaProcessor, ILuottokuntaOptions

class LuottokuntaProcessor( object ):

    implements(ILuottokuntaProcessor)
#    adapts(ISiteRoot)
    adapts(IStore)

    options_interface = ILuottokuntaOptions

    def __init__( self, context ):
        self.context = context

    def capture(self, order, price):
        # always returns async - just here to make the processor happy
        return keys.results_async

    def authorize( self, order, payment ):
        pass
