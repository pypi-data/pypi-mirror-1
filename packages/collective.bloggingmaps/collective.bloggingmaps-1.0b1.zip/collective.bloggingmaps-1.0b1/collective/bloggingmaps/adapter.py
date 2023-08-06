from zope.interface import implements
from zope.component import adapts

from Products.Maps.interfaces import IMarker
from Products.Maps.adapters import GeoLocation

from Products.ATContentTypes.interface import IATEvent


class LocationMarker(GeoLocation):
    implements(IMarker)
    adapts(IATEvent)

    @property
    def title(self):
        return self.context.location

    @property
    def description(self):
        return self.context.Description()

    @property
    def layers(self):
        return self.context.Subject()

    @property
    def icon(self):
        return self.context.getField('markerIcon').get(self.context)

    @property
    def url(self):
        return self.context.absolute_url()
    

    # rewrited becuause of missing accessors when using schema extender
    
    @property
    def _location(self):
        return self.context.getField('geolocation').get(self.context)
    
    @property
    def latitude(self):
        return self._location and self._location[0]

    @property
    def longitude(self):
        return self._location and self._location[1]
