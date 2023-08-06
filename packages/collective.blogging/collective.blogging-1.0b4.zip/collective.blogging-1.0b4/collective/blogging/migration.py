import logging
import transaction

from zope.interface import alsoProvides, noLongerProvides

from Products.CMFCore.utils import getToolByName

#BBB - see interfaces.py
from collective.blogging.interfaces import (IFolderMarker, IEntryMarker,
                                            IDocumentMarker, INewsItemMarker,
                                            IEventMarker, ILinkMarker,
                                            IImageMarker, IFileMarker,
                                            IBlogMarker)    

logger = logging.getLogger("collective.blogging")
PROFILE_ID = 'profile-collective.blogging:default'

#BBB - see interfaces.py
def fixEntryMarkup(context):
    logger.info("Starting migration of old blog entries markup to new one.")
    catalog = getToolByName(context, 'portal_catalog')
    ifaces = (IDocumentMarker, INewsItemMarker, IEventMarker, ILinkMarker,
                IImageMarker, IFileMarker)
    entry_brains = catalog(
        object_provides=[x.__identifier__ for x in ifaces],
        Language=u'all'
    )
    logger.info("Found %s blog enries with old markup.", len(entry_brains))
    for brain in entry_brains:
        try:
            entry = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("AttributeError getting entry object at %s",
                        brain.getURL())
            continue
        
        for iface in ifaces:
            if iface.providedBy(entry):
                noLongerProvides(entry, iface)
                logger.info('Markup "%s" removed from "%s".' % (iface.__identifier__,
                                                                brain.getPath()))
            
            if not IEntryMarker.providedBy(entry):
                alsoProvides(entry, IEntryMarker)
                logger.info('Markup "%s" set for "%s".' % (IEntryMarker.__identifier__,
                                                            brain.getPath()))
        
        entry.reindexObject()
    logger.info("Committing transaction after migrating entries markup.")
    transaction.commit()


def fixBlogMarkup(context):
    logger.info("Starting migration of old blogs markup to new one.")
    catalog = getToolByName(context, 'portal_catalog')
    blog_brains = catalog(
        object_provides=IFolderMarker.__identifier__,
        Language=u'all'
    )
    logger.info("Found %s blogs with old markup.", len(blog_brains))
    for brain in blog_brains:
        try:
            blog = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("AttributeError getting blog object at %s",
                        brain.getURL())
            continue
        
        if IFolderMarker.providedBy(blog):
            noLongerProvides(blog, IFolderMarker)
            logger.info('Markup "%s" removed from "%s".' % (IFolderMarker.__identifier__,
                                                            brain.getPath()))
            
        if not IBlogMarker.providedBy(blog):
            alsoProvides(blog, IBlogMarker)
            logger.info('Markup "%s" set for "%s".' % (IBlogMarker.__identifier__,
                                                        brain.getPath()))
    
        blog.reindexObject()
    
    logger.info("Committing transaction after migrating blogs markup.")
    transaction.commit()

def reindexPublishDates(context):
    logger.info("Starting reindex existing blog entries.")
    catalog = getToolByName(context, 'portal_catalog')
    entry_brains = catalog(
        object_provides=IEntryMarker.__identifier__,
        Language=u'all'
    )
    logger.info("Found %s blog enries with old publishing indexes.", len(entry_brains))
    for brain in entry_brains:
        try:
            entry = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("AttributeError getting entry object at %s",
                        brain.getURL())
            continue
        
        entry.reindexObject()
        logger.info('Entry "%s" reindexed.' % brain.getPath())
