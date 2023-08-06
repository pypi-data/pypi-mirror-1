from Products.ATContentTypes.interface import IATContentType, IATDocument, \
    IATEvent, IATNewsItem, IATFile, IATImage, IATLink
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Maps.adapters import GeoLocation
from Products.Maps.interfaces import IMarker, IRichMarker
from Products.Maps.interfaces.map import IMapView, IMap
from urllib2 import urlopen
from zope.component import adapts, getMultiAdapter
from zope.interface import implements
import urllib


class CoreRichMarker(GeoLocation):
    implements(IRichMarker)
    adapts(IATContentType)

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
    
    @property
    def base(self):
        return self.getCustomContent('base')
    
    def getCustomContent(self, name):
        view = getMultiAdapter((self.context, self.context.REQUEST), name=name)
        return view()
    
    def getMapContent(self, title, name):
        html = self.getCustomContent(name)
        if html:
            return {'title': title, 'text': html}
        else:
            return None

class EventRichMarker(CoreRichMarker):
    adapts(IATEvent)
    
    @property
    def contents(self):
        details = self.getMapContent(title = 'Event details', name='event_details')
        if details:
            return (details,)
        else:
            return tuple()


class NewsRichMarker(CoreRichMarker):
    adapts(IATNewsItem)
    
    @property
    def contents(self):
        image = self.getMapContent(title = 'Image', name='newsitem_details')
        if image:
            return (image,)
        else:
            return tuple()

""" the next classes are not actually needed, but in few days I'll use them to custom  the tabs of that types"""

class PageRichMarker(CoreRichMarker):
    adapts(IATDocument)
    
    @property
    def contents(self):
        return tuple()

class ImageRichMarker(CoreRichMarker):
    adapts(IATImage)
    
    @property
    def contents(self):
        return tuple()
    
class FileRichMarker(CoreRichMarker):
    adapts(IATFile)

    @property
    def contents(self):
        return tuple()
    
class LinkRichMarker(CoreRichMarker):
    adapts(IATLink)
    
    @property
    def contents(self):
        return tuple()

class MapSearchResults(object):
    adapts(IPloneSiteRoot)
    implements(IMap)

    def __init__(self, context):
        self.context = context
    
    def getMarkers(self):
        brains = self.context.queryCatalog(REQUEST=self.context.REQUEST)
        for brain in brains:
            x = brain.getObject()
            yield IMarker(x)
