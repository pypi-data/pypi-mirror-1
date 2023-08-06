from zope.interface import implements, alsoProvides, noLongerProvides
from zope.i18nmessageid import MessageFactory
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget

_ = MessageFactory('navrootfield')


def addMarkerInterface(obj, *ifaces):
    for iface in ifaces:
        if not iface.providedBy(obj):
            alsoProvides(obj, iface)

def removeMarkerInterface(obj, *ifaces):
    for iface in ifaces:
        if iface.providedBy(obj):
            noLongerProvides(obj, iface)

class InterfaceMarkerField(ExtensionField, BooleanField):
    def get(self, instance, **kwargs):
        return INavigationRoot.providedBy(instance)

    def getRaw(self, instance, **kwargs):
        return INavigationRoot.providedBy(instance)

    def set(self, instance, value, **kwargs):
        if value:
            addMarkerInterface(instance, INavigationRoot)
        else:
            removeMarkerInterface(instance, INavigationRoot)


class NavigationRoot(object):
    implements(ISchemaExtender)

    _fields = [
        InterfaceMarkerField(
            'navigation_root',
            schemata = "settings",
            widget = BooleanWidget(
                label = _(
                    u"label_navigation_root",
                    default=u"Navigation root"
                ),
                description = _(
                    u"help_navigation_root",
                    default=u"Make this object the navigation root."
                ),
            ),
        )
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields
