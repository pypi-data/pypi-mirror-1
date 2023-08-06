from logging import getLogger

from Products.CMFCore.utils import getToolByName

log = getLogger('collective.blogging')

INDEXES = {
    'publish_year' : 'FieldIndex',
    'publish_month': 'FieldIndex',
    'blogged'      : 'FieldIndex',
}

METADATA = [
    'publish_year',
    'publish_month',
]

def setupCatalog(context):

    if context.readDataFile('collective.blogging_various.txt') is None:
        return

    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')

    idxs = catalog.indexes()
    mtds = catalog.schema()
    
    for index in INDEXES.keys():
        if index not in idxs:
            catalog.addIndex(index, INDEXES[index])
            log.info('Catalog index "%s" installed' % index)
    
    for mt in METADATA:
        if mt not in mtds:
            catalog.addColumn(mt)
            log.info('Catalog metadata "%s" installed' % mt)

def setupViews(context):

    if context.readDataFile('collective.blogging_various.txt') is None:
        return

    portal = context.getSite()
    portal_types = getToolByName(portal, 'portal_types')

    # Folder views
    for ptype in ['Folder', 'Large Plone Folder', 'Topic']:
        type_info = portal_types.getTypeInfo(ptype)
        if 'blog-gallery' not in type_info.view_methods:
            type_info.view_methods = type_info.view_methods + ('blog-gallery',)
