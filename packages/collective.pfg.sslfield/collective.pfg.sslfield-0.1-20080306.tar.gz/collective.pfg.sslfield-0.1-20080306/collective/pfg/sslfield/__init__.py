
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from config import * 

try:
    from zope.i18nmessageid import MessageFactory
except ImportError:
    from Products.CMFPlone.messagefactory_ import PloneMessageFactory as PFGSSLFieldsFactory
else:
    PFGSSLFieldsFactory = MessageFactory('collective.pfg.sslfield')

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    import content

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

