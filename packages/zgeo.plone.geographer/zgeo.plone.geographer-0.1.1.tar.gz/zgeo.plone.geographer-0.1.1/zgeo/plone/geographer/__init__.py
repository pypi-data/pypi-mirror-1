from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from zgeo.plone.geographer import setuphandlers

registerIndexableAttribute(
    'zgeo_geometry',
    setuphandlers.zgeo_geometry_value
    )

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
