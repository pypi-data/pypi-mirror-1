from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from zgeo.geographer.interfaces import IGeoreferenced

def setupVarious(context):
    if context.readDataFile('zgeo.plone.atom_various.txt') is None:
        return
    portal = context.getSite()
