from zope.interface import implements
from zope.component import adapts

from archetypes.schemaextender.interfaces import (ISchemaExtender, IOrderableSchemaExtender,
                                                    IBrowserLayerAwareExtender)
from archetypes.schemaextender.field import ExtensionField
from archetypes.markerfield import InterfaceMarkerField

from Products.Archetypes.atapi import (TextField, IntegerField,
                                        BooleanField)
from Products.Archetypes.atapi import (BooleanWidget, TextAreaWidget,
                                        SelectionWidget)
from Products.ATContentTypes.interface import IATLink

from collective.blogging.interfaces import (IBloggable, IPostable, IBlogMarker,
                                            IEntryMarker, IBloggingSpecific)
from collective.blogging import _
from collective.blogging import BLOG_PERMISSION


class ExTextField(ExtensionField, TextField):
    """ A text field """

class ExBooleanField(ExtensionField, BooleanField):
    """ A boolean field """

class ExIntegerField(ExtensionField, IntegerField):
    """ An integer field """

class BlogExtender(object):
    """ Add blog configuration fields to all bloggable content. """
    adapts(IBloggable)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific
    
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
        
        ExBooleanField("enable_full",
            schemata = u'blog',
            languageIndependent = True,
            default = False,
            write_permission = BLOG_PERMISSION,
            widget = BooleanWidget(
                label = _(u"label_full_view", default=u"Full view"),
                description = _(u"help_full_view",
                    default = u"Tick this checkbox to display entry body text in the blog view."),
            ),        
        ),
        
        ExIntegerField("batch_size",
            schemata = u'blog',
            languageIndependent = True,
            default = 10,
            write_permission = BLOG_PERMISSION,
            enforceVocabulary = False,
            vocabulary = (3, 5, 10, 15, 20),
            widget = SelectionWidget(
                label = _(u"label_batch_size",
                    default=u"Batch size"),
                description = _(u"help_batch_size",
                    default = u"Select how many blog entries should be listed per page in the blog view."),
            ),
        ),
        
        ExBooleanField("enable_toolbar",
            schemata = u'blog',
            languageIndependent = True,
            default = True,
            write_permission = BLOG_PERMISSION,
            widget = BooleanWidget(
                label = _(u"label_enable_toolbar",
                    default = u"Toolbar enabled"),
                description = _(u"help_enable_toolbar",
                    default = u"Tick to enable / disable blog toolbar on the top of its page."),
            ),
        ),
        
        ExBooleanField("enable_count",
            schemata = u'blog',
            languageIndependent = True,
            default = True,
            write_permission = BLOG_PERMISSION,
            widget = BooleanWidget(
                label = _(u"label_enable_count",
                    default = u"Display count"),
                description = _(u"help_enable_count",
                    default = u"Tick to enable / disable blog contents count displaying."),
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


class EntryExtender(object):
    """ Add a new marker field to all possible entry types. """
    adapts(IPostable)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IEntryMarker,),
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
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [

        ExTextField('embedCode',
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
