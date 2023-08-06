from Products.ATContentTypes.interface import IATContentType, IATDocument, \
    IATEvent, IATNewsItem, IATFile, IATImage, IATLink
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot, IPloneSiteRoot
from Products.Maps.adapters import GeoLocation
from Products.Maps.interfaces import IMarker, IRichMarker
from Products.Maps.interfaces.map import IMapView, IMap
from urllib2 import urlopen
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts, getMultiAdapter
from zope.interface import implements
import urllib

class CoreRichMarker(GeoLocation):
    '''
    First of all we need to wake up the adapter and check the default values
    when location is not set
    >>> from zope.annotation.interfaces import IAnnotations
    >>> from zope.component import getAdapter
    >>> from Products.Maps.interfaces import IRichMarker
    >>> adapter = getAdapter(self.portal.news, IRichMarker)
    >>> adapter
    <redturtle.maps.core.adapter.CoreRichMarker object at ...>
    
    >>> adapter.gmapurl
    'http://maps.google.com/maps/geo?q=&output=csv&key=None'
    
    >>> adapter.status
    >>> adapter.accuracy
    >>> adapter.latitude
    >>> adapter.longitude

    >>> adapter.icon
    'Red Marker'

    Then we check what happens when we have something in the location
    
    
    >>> self.portal.news.setLocation('via Modena 19, Ferrara')
    >>> adapter = getAdapter(self.portal.news, IRichMarker)
    >>> adapter.gmapurl
    '...?q=via%20Modena%2019%2C%20Ferrara&output=csv&key=None'
    
    
    >>> adapter.annotations['maps_location']
    'via Modena 19, Ferrara'
    >>> adapter.annotations['maps_data']
    '200,8,44.8472706,11.5963263'
    
    >>> adapter.status
    '200'
    >>> adapter.accuracy
    '8'
    >>> adapter.latitude
    '44.8472706'
    >>> adapter.longitude
    '11.5963263'
    
    >>> annotations = IAnnotations(self.portal.news)
    >>> annotations == adapter.annotations
    True
    '''
    implements(IRichMarker)
    adapts(IATContentType)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
        self.config = getMultiAdapter((self.context,
                                       self.context.REQUEST),
                                       name="maps_configuration")
        #ip ='66.249.93.104'
        self.location = self.context.getLocation()
        # self.location = self.annotations.get('maps_location', '')
        
        if not self.location:
            self.setDefault()
        else:
            self.updateMapsData()
        
    def setDefault(self):
        '''
        Sets the default value for some adapter attributes
        '''
        self.lat = None
        self.lon = None
        self.status = None
        self.accuracy = None
    
    def updateMapsData(self):
        '''
        Get maps data from google and sets the adapter attributes 
        '''
        if self.location != self.annotations.get('maps_location'):
            page = urlopen(self.gmapurl).read()
            status, accuracy, latitude, longitude = page.split(',')
            self.annotations['maps_data'] = page
            self.annotations['maps_location'] = self.location
            
        status, accuracy, latitude, longitude = self.annotations['maps_data'].split(',')    
        self.lat = latitude
        self.lon = longitude
        self.status = status
        self.accuracy = accuracy
    
    @property
    def gmapurl(self):
        '''Returns the url to call to receive google geodata'''
        url = 'http://maps.google.com/maps/geo?q=%s&output=csv&key=%s' 
        return url % (urllib.quote(self.location), 
                      self.config.googlemaps_key)

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

""" the next classes are not actually needed, but in few days we could use them to customize the tabs of that types"""

class EventRichMarker(CoreRichMarker):
    adapts(IATEvent)
    
    @property
    def contents(self):
        return tuple()

class NewsRichMarker(CoreRichMarker):
    adapts(IATNewsItem)
    
    @property
    def contents(self):
        return tuple()
    

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
