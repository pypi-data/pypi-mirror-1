from logging import getLogger
from Products.CMFCore.utils import getToolByName
from plone.browserlayer import utils as layerutils
from collective.blogging.interfaces import IBloggingSpecific
from collective.blogging.interfaces import IEntryMarker, IBlogMarker

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

VIEW_TYPES = ['Folder', 'Large Plone Folder', 'Topic']
GALLERY_VIEW = u'blog-gallery'
FALLBACK_VIEW = u'atct_album_view'

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
            log.info('Catalog index "%s" installed.' % index)
    
    for mt in METADATA:
        if mt not in mtds:
            catalog.addColumn(mt)
            log.info('Catalog metadata "%s" installed.' % mt)

    # re-index blog content if exists (useful when reinstalling)
    blogs = catalog(object_provides=IBlogMarker.__identifier__)
    for blog in blogs:
        obj = blog.getObject()
        obj.reindexObject(idxs=INDEXES.keys())
    log.info('Reindexed %d blogs.' % len(blogs))
    
    entries = catalog(object_provides=IEntryMarker.__identifier__)
    for entry in entries:
        obj = entry.getObject()
        obj.reindexObject(idxs=INDEXES.keys())
    log.info('Reindexed %d entries.' % len(entries))


def resetCatalog(context):

    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return

    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')

    idxs = catalog.indexes()
    mtds = catalog.schema()
    
    for index in INDEXES.keys():
        if index in idxs:
            catalog.delIndex(index)
            log.info('Catalog index "%s" removed.' % index)
    
    for mt in METADATA:
        if mt in mtds:
            catalog.delColumn(mt)
            log.info('Catalog metadata "%s" removed.' % mt)

def setupViews(context):

    if context.readDataFile('collective.blogging_various.txt') is None:
        return

    portal = context.getSite()
    portal_types = getToolByName(portal, 'portal_types')

    # Folder views
    for ptype in VIEW_TYPES:
        type_info = portal_types.getTypeInfo(ptype)
        if GALLERY_VIEW not in type_info.view_methods:
            type_info.view_methods = type_info.view_methods + (GALLERY_VIEW,)
            log.info('"%s" view installed for %s.' % (GALLERY_VIEW, ptype))


def resetViews(context):

    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return

    portal = context.getSite()
    portal_types = getToolByName(portal, 'portal_types')

    # Folder views
    for ptype in VIEW_TYPES:
        type_info = portal_types.getTypeInfo(ptype)
        if GALLERY_VIEW in type_info.view_methods:
            type_info.view_methods = tuple([vm for vm in type_info.view_methods if vm !=GALLERY_VIEW])
            log.info('"%s" view uninstalled for %s.' % (GALLERY_VIEW, ptype))
    
    # This is how you can fix broken gallery folders due to assigned removed layout
    # it is commented out here because we don't want to call it during package "reinstall"
    """
    catalog = getToolByName(portal, 'portal_catalog')
    content = catalog(portal_type=VIEW_TYPES)
    for brain in content:
        obj = brain.getObject()
        if obj.getLayout() == GALLERY_VIEW:
            obj.setLayout(FALLBACK_VIEW)
            log.info('Default "%s" layout set for "%s".' % (FALLBACK_VIEW, '/'.join(obj.getPhysicalPath())))
    """

def resetLayers(context):
    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return
    
    if IBloggingSpecific in layerutils.registered_layers():
        layerutils.unregister_layer(name='collective.blogging')
        log.info('Browser layer "collective.blogging" uninstalled.')


def resetRoles(context):
    if context.readDataFile('collective.blogging_uninstall.txt') is None:
        return
    
    portal = context.getSite()
    portal._delRoles(['Blogger'])
    log.info('"Blogger" security role removed.')
