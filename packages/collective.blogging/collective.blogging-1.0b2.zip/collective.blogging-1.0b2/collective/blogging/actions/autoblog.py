from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.interface import Interface, implements

from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFPlone import PloneMessageFactory as _


class IAutoBlogAction(Interface):
    """Definition of the configuration
    """

class AutoBlogAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IAutoBlogAction, IRuleElementData)

    element = 'collective.blogging.actions.AutoBlog'

    @property
    def summary(self):
        return _(u"Enable auto-blogging")

class AutoBlogActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IAutoBlogAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        blog_field = obj.getField('blog_folder')
        entry_field = obj.getField('blog_entry')
        
        if blog_field:
            blog_field.set(obj, True)
        
        if entry_field:
            entry_field.set(obj, True)
        
        return True


class AutoBlogAddForm(NullAddForm):
    """A degenerate "add form"" for auto blog actions.
    """
    
    def create(self):
        return AutoBlogAction()
