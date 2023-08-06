from zope.i18nmessageid import MessageFactory
from Products.CMFCore.permissions import setDefaultRoles

# import monkeys
from collective.blogging import patch

## LinguaPlone addon?
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    HAS_LINGUA_PLONE = False
else:
    HAS_LINGUA_PLONE = True
    del registerType

_ = MessageFactory("collective.blogging")

BLOG_PERMISSION = 'collective.blogging: Blog'

def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    setDefaultRoles(BLOG_PERMISSION, ())
