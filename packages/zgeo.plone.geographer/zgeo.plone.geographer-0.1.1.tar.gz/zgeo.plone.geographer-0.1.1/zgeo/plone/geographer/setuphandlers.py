from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from zgeo.geographer.interfaces import IGeoreferenced

def setupVarious(context):
    if context.readDataFile('zgeo.plone.geographer_various.txt') is None:
        return
    portal = context.getSite()
    addMetadataToCatalog(portal)

def zgeo_geometry_value(object, portal, **kwargs):
    try:
        geo = IGeoreferenced(object)
        return dict(type=geo.type, coordinates=geo.coordinates)
    except (ComponentLookupError, TypeError, ValueError, KeyError, IndexError):
 	# The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

def addMetadataToCatalog(portal):
    cat = getToolByName(portal, 'portal_catalog', None)
    metadata = ('zgeo_geometry',)
    reindex = []
    if cat is not None:
        for column in metadata:
            if column in cat.schema():
                continue
            cat.addColumn(column)
            reindex.append(column)
        if reindex:
            cat.refreshCatalog()
