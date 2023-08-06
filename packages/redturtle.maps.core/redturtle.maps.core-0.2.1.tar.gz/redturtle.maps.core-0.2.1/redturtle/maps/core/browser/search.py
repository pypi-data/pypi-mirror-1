from Products.Maps.browser.map import BaseMapView
from Products.Maps.interfaces.map import IMapView, IMap
from zope.interface import implements
    
class MapSearch(BaseMapView):
    """
    Search results view class.
    """    
    implements(IMapView, )
            
    @property
    def enabled(self):
        if self.map is None:
            return False
        return True            
            