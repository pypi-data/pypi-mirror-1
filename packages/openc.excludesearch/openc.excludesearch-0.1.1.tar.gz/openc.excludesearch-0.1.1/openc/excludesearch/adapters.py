from zope.component import adapts
from zope.interface import implements, providedBy, alsoProvides, noLongerProvides
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.public import BooleanWidget
from Products.ATContentTypes.content.document import ATDocument

from Products.Archetypes.public import BooleanField
from archetypes.schemaextender.field import ExtensionField
from Products.ATContentTypes.interface.interfaces import IATContentType

from openc.excludesearch.interfaces import IExcludeFromSearch

class InterfaceMarkerField(ExtensionField, BooleanField):
    def get(self, instance, **kwargs):
        return IExcludeFromSearch.providedBy(instance)

    def getRaw(self, instance, **kwargs):
        return IExcludeFromSearch.providedBy(instance)

    def set(self, instance, value, **kwargs):
        if value:
            addMarkerInterface(instance, IExcludeFromSearch)
        else:
            removeMarkerInterface(instance, IExcludeFromSearch)


def addMarkerInterface(obj, *ifaces):
    for iface in ifaces:
        if not iface.providedBy(obj):
            alsoProvides(obj, iface)


def removeMarkerInterface(obj, *ifaces):
    for iface in ifaces:
        if iface.providedBy(obj):
            noLongerProvides(obj, iface)



class HideInSearchOption(object):
    adapts(IATContentType)          
    implements(ISchemaExtender)


    fields = [
        InterfaceMarkerField("hidesearch",
        widget = BooleanWidget(
            label="Hide this page in search",
            description="Prevent this item displaying in search results"),
        schemata="settings"),
        ]

    def __init__(self, context):
         self.context = context

    def getFields(self):
         return self.fields
