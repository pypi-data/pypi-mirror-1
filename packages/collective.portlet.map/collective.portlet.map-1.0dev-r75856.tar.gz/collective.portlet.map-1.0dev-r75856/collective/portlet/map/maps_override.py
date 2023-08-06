from zope.interface import implements

from Products.Maps.browser.map import BaseMapView
from Products.Maps.interfaces import IMapView

class FolderMapView(BaseMapView):
    implements(IMapView)

    @property
    def enabled(self):
        if self.map is None:
            return False
        return True