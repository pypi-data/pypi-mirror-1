from zope.interface import implements
from zope.component import adapts

from archetypes.schemaextender.interfaces import (ISchemaExtender,
                                                    IOrderableSchemaExtender)
from archetypes.schemaextender.field import ExtensionField
from archetypes.markerfield import InterfaceMarkerField

from Products.Archetypes.atapi import (TextField, IntegerField,
                                        BooleanField)
from Products.Archetypes.atapi import (BooleanWidget, TextAreaWidget,
                                        SelectionWidget)
from Products.Archetypes.utils import IntDisplayList

from Products.ATContentTypes.interface import IATDocument
from Products.ATContentTypes.interface import IATEvent
from Products.ATContentTypes.interface import IATFile
from Products.ATContentTypes.interface import IATFolder
from Products.ATContentTypes.interface import IATBTreeFolder
from Products.ATContentTypes.interface import IATImage
from Products.ATContentTypes.interface import IATLink
from Products.ATContentTypes.interface import IATNewsItem
from Products.ATContentTypes.interface import IATTopic

from collective.blogging.interfaces import IBlogMarker, IFolderMarker
from collective.blogging.interfaces import IDocumentMarker
from collective.blogging.interfaces import INewsItemMarker
from collective.blogging.interfaces import IEventMarker
from collective.blogging.interfaces import ILinkMarker
from collective.blogging.interfaces import IImageMarker
from collective.blogging.interfaces import IFileMarker
from collective.blogging import _
from collective.blogging import BLOG_PERMISSION


class EmbedField(ExtensionField, TextField):
    """ An embed content field """

class BatchSizeField(ExtensionField, IntegerField):
    """ A batch size field """
    
    @property
    def default(self):
        return 10
    
    @property
    def schemata(self):
        return "blog"
    
    @property
    def write_permission(self):
        return BLOG_PERMISSION
    
    @property
    def languageIndependent(self):
        return True
    
    @property
    def enforceVocabulary(self):
        return True

    def Vocabulary(self, content_instance):
        return IntDisplayList((
            (3, 3),
            (5, 5),
            (10, 10),
            (15, 15),
            (20, 20),
        ))

class EnableToolbarField(ExtensionField, BooleanField):
    """ A boolean field for enabling blog toolbar """
    
    @property
    def default(self):
        return True
    
    @property
    def schemata(self):
        return "blog"
    
    @property
    def write_permission(self):
        return BLOG_PERMISSION
    
    @property
    def languageIndependent(self):
        return True

class FolderExtender(object):
    """ Add a new marker field to all ATFolder based types. """
    adapts(IATFolder)
    implements(IOrderableSchemaExtender)

    fields = [
        InterfaceMarkerField("blog_folder",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IFolderMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_enabled",
                    default=u"Blog enabled"),
                description = _(u"help_blog_enabled",
                    default=u"Tick to enable / disable blog behaviour."),
            ),
        ),
        
        BatchSizeField("batch_size",
            widget = SelectionWidget(
                label = _(u"label_batch_size",
                    default=u"Batch size"),
                description = _(u"help_batch_size",
                    default = u"Select how many blog entries should be listed per page in the blog view."),
            ),
        ),
        
        EnableToolbarField("enable_toolbar",
            widget = BooleanWidget(
                label = _(u"label_enable_toolbar",
                    default = u"Toolbar enabled"),
                description = _(u"help_enable_toolbar",
                    default = u"Tick to enable / disable blog toolbar on the top of its page."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
    
    def getOrder(self, original):
        blog = original['blog']
        blog.remove('blog_folder')
        blog.insert(0, 'blog_folder')
        return original

class LargeFolderExtender(object):
    """ Add a new marker field to all ATBTreeFolder based types. """
    adapts(IATBTreeFolder)
    implements(IOrderableSchemaExtender)

    fields = [
        InterfaceMarkerField("blog_folder",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IFolderMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_enabled",
                    default=u"Blog enabled"),
                description = _(u"help_blog_enabled",
                    default=u"Tick to enable / disable blog behaviour."),
            ),
        ),
        
        BatchSizeField("batch_size",
            widget = SelectionWidget(
                label = _(u"label_batch_size",
                    default=u"Batch size"),
                description = _(u"help_batch_size",
                    default = u"Select how many blog entries should be listed per page in the blog view."),
            ),
        ),
        
        EnableToolbarField("enable_toolbar",
            widget = BooleanWidget(
                label = _(u"label_enable_toolbar",
                    default = u"Toolbar enabled"),
                description = _(u"help_enable_toolbar",
                    default = u"Tick to enable / disable blog toolbar on the top of its page."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
    
    def getOrder(self, original):
        blog = original['blog']
        blog.remove('blog_folder')
        blog.insert(0, 'blog_folder')
        return original


class TopicExtender(object):
    """ Add a new marker field to all ATTopic based types. """
    adapts(IATTopic)
    implements(IOrderableSchemaExtender)

    fields = [
        InterfaceMarkerField("blog_folder",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IBlogMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_enabled",
                    default=u"Blog enabled"),
                description = _(u"help_blog_enabled",
                    default=u"Tick to enable / disable blog behaviour."),
            ),
        ),
        
        BatchSizeField("batch_size",
            widget = SelectionWidget(
                label = _(u"label_batch_size",
                    default=u"Batch size"),
                description = _(u"help_batch_size",
                    default = u"Select how many blog entries should be listed per page in the blog view."),
            ),
        ),
        
        EnableToolbarField("enable_toolbar",
            widget = BooleanWidget(
                label = _(u"label_enable_toolbar",
                    default = u"Toolbar enabled"),
                description = _(u"help_enable_toolbar",
                    default = u"Tick to enable / disable blog toolbar on the top of its page."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
    
    def getOrder(self, original):
        blog = original['blog']
        blog.remove('blog_folder')
        blog.insert(0, 'blog_folder')
        return original


class DocumentExtender(object):
    """ Add a new marker field to all ATDocument based types. """
    adapts(IATDocument)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IDocumentMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_entry",
                    default=u"Blog Entry"),
                description = _(u"help_blog_entry_marker",
                    default=u"Mark this content as blog entry."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class NewsItemExtender(object):
    """ Add a new marker field to all ATNewsItem based types. """
    adapts(IATNewsItem)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (INewsItemMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_entry",
                    default=u"Blog Entry"),
                description = _(u"help_blog_entry_marker",
                    default=u"Mark this content as blog entry."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class EventExtender(object):
    """ Add a new marker field to all ATEvent based types. """
    adapts(IATEvent)
    implements(IOrderableSchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IEventMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_entry",
                    default=u"Blog Entry"),
                description = _(u"help_blog_entry_marker",
                    default=u"Mark this content as blog entry."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
    
    def getOrder(self, original):
        blog = original['blog']
        blog.remove('blog_entry')
        blog.insert(0, 'blog_entry')
        return original

class LinkExtender(object):
    """ Add a new marker field to all ATLink based types. """
    adapts(IATLink)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (ILinkMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_entry",
                    default=u"Blog Entry"),
                description = _(u"help_blog_entry_marker",
                    default=u"Mark this content as blog entry."),
            ),
        ),

        EmbedField('embedCode',
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            default='',
            default_content_type = 'text/plain',
            allowable_content_types = ('text/plain',),
            widget=TextAreaWidget(
                label=_(u'label_embed', default=u'Embed'),
                description=_(u'help_embed',
                              default=u'Paste embed code for example youtube, google or other video content.'),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class ImageExtender(object):
    """ Add a new marker field to all ATImage based types. """
    adapts(IATImage)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IImageMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_entry",
                    default=u"Blog Entry"),
                description = _(u"help_blog_entry_marker",
                    default=u"Mark this content as blog entry."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class FileExtender(object):
    """ Add a new marker field to all ATFile based types. """
    adapts(IATFile)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IFileMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_entry",
                    default=u"Blog Entry"),
                description = _(u"help_blog_entry_marker",
                    default=u"Mark this content as blog entry."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
