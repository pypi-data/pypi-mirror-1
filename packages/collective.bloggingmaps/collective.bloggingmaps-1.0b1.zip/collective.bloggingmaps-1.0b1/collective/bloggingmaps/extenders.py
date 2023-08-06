from zope.interface import implements
from zope.component import adapts, getMultiAdapter

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField
from archetypes.markerfield import InterfaceMarkerField

from Products.Archetypes.atapi import (StringField, BooleanField,
                                        BooleanWidget, SelectionWidget)
from Products.Archetypes.utils import DisplayList


from Products.ATContentTypes.interface import (IATFolder, IATBTreeFolder,
                                                IATEvent, IATTopic)

from Products.Maps.field import LocationField, LocationWidget
from Products.Maps.interfaces import IMapEnabled

from collective.blogging import BLOG_PERMISSION
from collective.blogging.interfaces import IBloggingSpecific
from collective.bloggingmaps import _

class ShowMapField(ExtensionField, BooleanField):
    """ An simple boolean field """

class GeoLocationField(ExtensionField, LocationField):
    """ An map location field """

class MarkerIconField(ExtensionField, StringField):
    """ A map marker icon field """

    def getDefault(self, content_instance):
        config = getMultiAdapter((content_instance, content_instance.REQUEST),
                                    name="maps_configuration")
        return config.default_location

    @property
    def enforceVocabulary(self):
        return True

    def Vocabulary(self, content_instance):
        config = getMultiAdapter((content_instance, content_instance.REQUEST),
                                    name="maps_configuration")
        marker_icons = config.marker_icons
        result = DisplayList()
        for icon in marker_icons:
            result.add(icon['name'], icon['name'])
        return result


class MapExtender(object):
    """ Add a new map location field to all ATEvent based types. """
    adapts(IATEvent)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [
        ShowMapField(
            'show_map',
            schemata = u'blog',
            languageIndependent = True,
            write_permission = BLOG_PERMISSION,
            required = False,
            default = False,
            widget = BooleanWidget(
                label=_(u'label_showmap', default = u'Show map'),
                description = _(u'help_showmap',
                                default = u'Tick the checkbox explicitly to show map on the entry page.')
            )
        ),
        
        GeoLocationField(
            'geolocation',
            schemata = "blog",
            languageIndependent = True,
            write_permission = BLOG_PERMISSION,
            required=False,
            validators=('isGeoLocation',),
            widget=LocationWidget(
                label='Location',
                label_msgid='label_geolocation',
                description_msgid='help_geolocation',
                i18n_domain='maps',
            ),
        ),

        MarkerIconField(
            'markerIcon',
            schemata = "blog",
            languageIndependent = True,
            write_permission = BLOG_PERMISSION,
            widget=SelectionWidget(
                format="select",
                label='Marker icon',
                label_msgid='label_markericon',
                description_msgid='help_markericon',
                i18n_domain='maps',
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class FolderExtender(object):
    """ Add a new marker field to all ATFolder based types. """
    adapts(IATFolder)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [
        InterfaceMarkerField("enable_maps",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IMapEnabled,),
            widget = BooleanWidget(
                label = _(u"label_enable_maps",
                    default=u"Maps enabled"),
                description = _(u"help_enable_maps",
                    default=u"Enable entry maps to be available in the blog view."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class LargeFolderExtender(object):
    """ Add a new marker field to all ATBTreeFolder based types. """
    adapts(IATBTreeFolder)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [
        InterfaceMarkerField("enable_maps",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IMapEnabled,),
            widget = BooleanWidget(
                label = _(u"label_enable_maps",
                    default=u"Maps enabled"),
                description = _(u"help_enable_maps",
                    default=u"Enable entry maps to be available in the blog view."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class TopicExtender(object):
    """ Add a new marker field to all ATTopic based types. """
    adapts(IATTopic)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [
        InterfaceMarkerField("enable_maps",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IMapEnabled,),
            widget = BooleanWidget(
                label = _(u"label_enable_maps",
                    default=u"Maps enabled"),
                description = _(u"help_enable_maps",
                    default=u"Enable entry maps to be available in the blog view."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
