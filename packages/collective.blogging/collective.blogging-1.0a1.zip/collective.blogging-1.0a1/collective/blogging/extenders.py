from zope.interface import implements
from zope.component import adapts

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from archetypes.markerfield import InterfaceMarkerField

from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import (BooleanWidget, TextAreaWidget)
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

class FolderExtender(object):
    """ Add a new marker field to all ATFolder based types. """
    adapts(IATFolder)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_folder",
            schemata = "settings",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IFolderMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog",
                    default=u"Blog"),
                description = _(u"help_blog_marker",
                    default=u"Mark this content as blog."),
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
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_folder",
            schemata = "settings",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IFolderMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog",
                    default=u"Blog"),
                description = _(u"help_blog_marker",
                    default=u"Mark this content as blog."),
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
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_folder",
            schemata = "settings",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IBlogMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog",
                    default=u"Blog"),
                description = _(u"help_blog_marker",
                    default=u"Mark this content as blog."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class DocumentExtender(object):
    """ Add a new marker field to all ATDocument based types. """
    adapts(IATDocument)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
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
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
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

class LinkExtender(object):
    """ Add a new marker field to all ATLink based types. """
    adapts(IATLink)
    implements(ISchemaExtender)

    fields = [
        InterfaceMarkerField("blog_entry",
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
