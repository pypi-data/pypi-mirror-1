from zope.interface import implements
from zope.component import getMultiAdapter
from zope import schema
from zope.formlib import form

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.blogging import HAS_LINGUA_PLONE, BLOG_PERMISSION
from collective.blogging import _
from collective.blogging.interfaces import IFolderMarker

class IManagePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    target_blog = schema.Choice(title=_(u"Target blog"),
        description=_(u"Find the blog which will be this portlet used for."),
        required=True,
        source=SearchableTextSourceBinder({'object_provides' : IFolderMarker.__identifier__},
            default_query='path:'))

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IManagePortlet)

    target_blog=None

    def __init__(self, target_blog=None):
        self.target_blog = target_blog

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        blog_title = self.target_blog and self.target_blog.title()
        return _(u"Manage Blog: ${blog}", mapping={'blog':blog_title})


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('manage.pt')
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')

    @property
    def available(self):
        anon = self.portal_state.anonymous()
        allowed = self.tools.membership().checkPermission(BLOG_PERMISSION, self.context)
        return (not anon) and allowed and self.blog() or False

    @property
    def blog_url(self):
        blog = self.blog()
        if blog is None:
            return None
        else:
            return blog.absolute_url()
    
    @property
    def addable_types(self):
        blog = self.blog()
        return blog and blog.getRawLocallyAllowedTypes()
    
    @memoize
    def blog(self):
        """ Get the blog the portlet is pointing to """
        
        blog_path = self.data.target_blog
        if not blog_path:
            return None

        if blog_path.startswith('/'):
            blog_path = blog_path[1:]
        
        if not blog_path:
            return None
        portal = self.portal_state.portal()
        obj = portal.restrictedTraverse(blog_path, default=None)
        if HAS_LINGUA_PLONE:
            return obj and obj.getLanguage() == self.request.get('LANGUAGE') and obj or None
        return obj

    @property
    def portal_url(self):
        return self.portal_state.portal_url()
    
    def header(self):
        blog_title = self.blog() and self.blog().title
        return _(u"Manage Blog: ${blog}", mapping={'blog':blog_title})

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IManagePortlet)
    form_fields['target_blog'].custom_widget = UberSelectionWidget
    
    label = _(u"Add Manage Blog portlet")
    description = _(u"This portlet helps to manage blog's content.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(IManagePortlet)
    form_fields['target_blog'].custom_widget = UberSelectionWidget

    label = _(u"Edit Manage Blog portlet")
    description = _(u"This portlet helps to manage blog's content.")
