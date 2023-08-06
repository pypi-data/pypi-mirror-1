from zope.interface import implements
from zope.component import getMultiAdapter
from zope import schema
from zope.formlib import form
from zope.i18n import translate

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as PMF

from collective.blogging import HAS_LINGUA_PLONE, BLOG_PERMISSION
from collective.blogging import _
from collective.blogging.interfaces import IFolderMarker

class IManagePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    target_blog = schema.Choice(
        title=_(u"Target blog"),
        description=_(u"Find the blog which will be this portlet used for."),
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides' : IFolderMarker.__identifier__},
            default_query='path:'
        )
    )
    
    addable_types = schema.Tuple(
        title=_(u"Addable types"),
        description=_(u"Select content types for which you would like to show create link in the portlet."),
        required=False,
        missing_value=set(),
        value_type=schema.Choice(
            vocabulary='plone.app.vocabularies.ReallyUserFriendlyTypes'
        )
    )

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IManagePortlet)

    target_blog = None
    addable_types = ()
    
    def __init__(self, target_blog=None, addable_types=()):
        self.target_blog = target_blog
        self.addable_types = addable_types
    
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
    def creation_links(self):
        blog = self.blog()
        result = []
        if blog:
            types = self.tools.types()
            blog_url = blog.absolute_url()
            portal_url = self.portal_state.portal_url()
            allowed = blog.getRawLocallyAllowedTypes()
            for item in self.data.addable_types:
                if item in allowed:
                    ti = types.getTypeInfo(item)
                    result.append({
                        'id'         : item,
                        'title'      : ti.title,
                        'description': translate(PMF(ti.description), context=self.request),
                        'icon'       : '%s/%s' % (portal_url, ti.getIcon()),
                        'url'        : '%s/createObject?type_name=%s' % (blog_url, item)
                    })
        return result
    
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
            return obj.getTranslation()
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
