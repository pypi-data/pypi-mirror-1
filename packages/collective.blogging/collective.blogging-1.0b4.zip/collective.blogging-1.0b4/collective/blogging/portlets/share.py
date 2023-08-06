from string import Template
from urllib import urlencode

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements
from zope.formlib import form
from zope.schema import List, Choice, TextLine

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.blogging.interfaces import IEntryMarker
from collective.blogging import _

PROVIDERS = [
    {'id':'Del.icio.us','url':'http://del.icio.us/post?url=$url&amp;title=$title','logo':'++resource++collective.blogging.static/delicious.png'},
    {'id':'Facebook','url':'http://www.facebook.com/share.php?u=$url','logo':'++resource++collective.blogging.static/facebook.png'},
    {'id':'Google Bookmarks','url':'http://www.google.com/bookmarks/mark?op=add&bkmk=$url&title=$title','logo':'++resource++collective.blogging.static/google.png'},
    {'id':'Yahoo Bookmarks','url':'http://bookmarks.yahoo.com/toolbar/savebm?opener=tb&amp;u=$url&amp;t=$title','logo':'++resource++collective.blogging.static/yahoo.png'},
    {'id':'Twitter','url':'http://twitter.com/home?status=$url','logo':'++resource++collective.blogging.static/twitter.png'},
    {'id':'MySpace','url':'http://www.myspace.com/Modules/PostTo/Pages/?c=$url&amp;t=$title','logo':'++resource++collective.blogging.static/myspace.png'},
    {'id':'Digg','url':'http://digg.com/submit?phase=2&amp;url=$url&amp;title=$title','logo':'++resource++collective.blogging.static/digg.png'},
    {'id':'Slashdot','url':'http://slashdot.org/bookmark.pl?title=$title&amp;url=$url','logo':'++resource++collective.blogging.static/slashdot.png'},
    {'id':'Live','url':'https://favorites.live.com/quickadd.aspx?marklet=1&amp;mkt=en-us&amp;url=$url&amp;title=$title&amp;top=1','logo':'++resource++collective.blogging.static/live.png'},
    {'id':'LinkedIn', 'url':'http://www.linkedin.com/shareArticle?mini=true&amp;url=$url&amp;title=$title','logo':'++resource++collective.blogging.static/linkedin.png'},
]

class ProvidersVocabulary(object):
    """"""
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [SimpleTerm(p.get('id'), p.get('id'), p.get('id'))
                    for p in PROVIDERS]
        return SimpleVocabulary(items)

ProvidersVocabularyFactory = ProvidersVocabulary()

class ISharePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    name = TextLine(
        required = False,
        title = _(u"Portlet title"),
        description = _(u"Enter portlet tile.")
    )

    restrict_types = List(
        required = False,
        title = _(u"Restrict by types"),
        description = _(u"Restrict portlet availability by content types wich entries are based on."),
        value_type = Choice(vocabulary =
            'plone.app.vocabularies.ReallyUserFriendlyTypes'),
    )
    
    providers = List(
        required = True,
        title = _(u"Providers"),
        description = _(u"Select enabled sharing services."),
        value_type = Choice(vocabulary =
            'collective.blogging.SharingProviders'),
    )

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISharePortlet)
    
    name = u''
    restrict_types = []
    providers = []
    
    def __init__(self, name=u'', restrict_types=[], providers=[]):
        self.name = name
        self.restrict_types = restrict_types
        self.providers = providers
    
    @property
    def title(self):
        return self.name or _(u'Share post')

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('share.pt')
    
    @property
    def available(self):
        if not IEntryMarker.providedBy(self.context):
            return False
        if self.context.portal_type not in self.data.restrict_types:
            return False
        return True

    def header(self):
        return self.data.name or _(u'Share post')
    
    def providers(self):
        result = []
        obj = aq_inner(self.context)
        url = obj.absolute_url()
        title = obj.title
        for p in PROVIDERS:
            if p.get('id') in self.data.providers:
                p_url = Template(p['url']).safe_substitute(url=url, title=title)
                result.append({
                    'id': p['id'],
                    'logo':p['logo'],
                    'url':p_url
                })
        return result

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISharePortlet)
    
    label = _(u"Add Share Entry portlet")
    description = _(u"This portlet renders link(s) to share an entry.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(ISharePortlet)

    label = _(u"Edit Share Entry portlet")
    description = _(u"This portlet renders link(s) to share an entry.")
