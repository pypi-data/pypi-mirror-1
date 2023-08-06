from Products.ATContentTypes.interface import IATContentType
from Products.Maps.interfaces import IMap, IMarker
from zope.component import adapts
from zope.interface import implements

class BaseItem(object):
    adapts(IATContentType)
    implements(IMap)

    def __init__(self, context):
        self.context = context
    
    def getMarkers(self):
        results = []
        marker = IMarker(self.context, None)
        if marker:
            results.append(marker)
        return results
        
    