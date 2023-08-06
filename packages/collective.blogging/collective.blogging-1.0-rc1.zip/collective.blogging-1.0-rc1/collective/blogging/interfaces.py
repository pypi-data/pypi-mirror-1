from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IBlog(Interface):
    """ A content which can contain blog entries, usually folders. """

class IBloggable(Interface):
    """ A content which can list blog entries, usually folders or smart folders. """

class IPostable(Interface):
    """ A content which can be posted as blog entry. """

# markers
class IBlogMarker(Interface):
    """ A content which can act like a blog """

class IEntryMarker(Interface):
    """ A generic blog entry """

class IBloggingSpecific(IDefaultPloneLayer):
    """ A marker interface that defines a Zope 3 browser layer. """

# BBB - all these interfaces are obsolete and should
# be removed before first release candidate

class IFolderMarker(IBlogMarker):
    """ A blog folderish content """

class IDocumentMarker(IEntryMarker):
    """ A document based blog entry """

class INewsItemMarker(IEntryMarker):
    """ A news item based blog entry """

class IEventMarker(IEntryMarker):
    """ An event based blog entry """

class ILinkMarker(IEntryMarker):
    """ A link based blog entry """

class IImageMarker(IEntryMarker):
    """ An image based blog entry """

class IFileMarker(IEntryMarker):
    """ An file based blog entry """
