from cStringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Archetypes.Extensions.utils import install_subskin


from collective.pfg.sslfield.config import *

def install(self):
    out = StringIO()

    portal = getToolByName(self,'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    setup_tool = getToolByName(portal, 'portal_setup')


    for dependency in DEPENDENCIES:
        print >> out, "Installing dependency %s:" % dependency
        quickinstaller.installProduct(dependency)
        import transaction
        transaction.savepoint(optimistic=True)


    if getFSVersionTuple()[:3]>=(3,0,0):
        setup_tool.runAllImportStepsFromProfile(
            'profile-collective.pfg.sslfield:default',
            purge_old=False)

    else:

        setup_tool.setImportContext('profile-collective.pfg.sslfield:default')
        setup_tool.runAllImportSteps()
        setup_tool.setImportContext('profile-CMFPlone:plone')

    install_subskin(self, out, GLOBALS)

    print >> out, "Installation completed."
    return out.getvalue()

def uninstall(self, reinstall=False):
    out = StringIO()

    print >>out, 'Nothing to be done'

    return out.getvalue()
