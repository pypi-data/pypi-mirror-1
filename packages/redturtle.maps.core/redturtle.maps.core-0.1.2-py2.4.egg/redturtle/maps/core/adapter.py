from zope.component import getMultiAdapter
from zope.interface import implements
from Products.Maps.interfaces import IMarker
from Products.Maps.adapters import GeoLocation
from urllib2 import urlopen
import urllib

class CoreRichMarker(GeoLocation):
    implements(IMarker)

    def __init__(self, context):
        self.context = context
        self.config = getMultiAdapter((self.context, 
                                       self.context.REQUEST), 
                                       name="maps_configuration")
        #ip ='66.249.93.104'
        self.location = self.context.getLocation()
        try:
            status, accuracy, latitude, longitude = self.location.split(',')
        except ValueError:
            location = urllib.quote(self.location)
            if not location:
                self.lat = latitude = self.lon = None
                return        
            url = 'http://maps.google.com/maps/geo?q=%s&output=csv&key=%s' % (location, self.config.googlemaps_key)
            page = urlopen(url).read()
            status, accuracy, latitude, longitude = page.split(',')
            self.context.setLocation(page)
            
        self.lat = latitude
        self.lon = longitude
        
    @property
    def latitude(self):
        return self.lat

    @property
    def longitude(self):
        return self.lon

    @property
    def title(self):
        return self.context.title_or_id()

    @property
    def description(self):
        return self.context.Description()

    @property
    def layers(self):
        return self.context.Subject()

    @property
    def icon(self):
        marker_icons = self.config.marker_icons
        return marker_icons[0]['name']

    @property
    def url(self):
        return self.context.absolute_url()

    @property
    def related_items(self):
        return tuple()

    @property
    def contents(self):
        return tuple()
