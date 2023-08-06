from Products.Maps.browser.map import BaseMapView as BaseView
from Products.Maps.interfaces import IMapView
from zope.interface import implements
from zope.component._api import getMultiAdapter

class DefaultMapView(BaseView):
    implements(IMapView)

    @property
    def enabled(self):
        plone = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        if self.map is None:
            return False
        if plone.is_view_template() and [m for m in self.map.getMarkers() if m.lon]:
            return True
        return False
    