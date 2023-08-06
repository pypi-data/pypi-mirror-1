from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class BlogMacros(BrowserView):
    """ Helper macros view """
    
    template = ViewPageTemplateFile('blog_macros.pt')
    
    @property
    def macros(self):
        return self.template.macros

class EntryMacros(BrowserView):
    """ Helper macros view """
    
    template = ViewPageTemplateFile('entry_macros.pt')
    
    @property
    def macros(self):
        return self.template.macros
