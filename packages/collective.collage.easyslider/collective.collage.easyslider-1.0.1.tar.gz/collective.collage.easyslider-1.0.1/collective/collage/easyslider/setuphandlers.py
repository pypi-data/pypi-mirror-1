from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from config import DEPENDENCIES
import transaction

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('collective.collage.easyslider_various.txt') is None:
        return

    # Add additional setup code here
    out = StringIO()
    portal = getSite()

    # Get portal_quickinstaller and install all dependencies
    qi = getToolByName(portal, 'portal_quickinstaller')
    installed_prods = [i['id'] for i in \
                       portal.portal_quickinstaller.listInstalledProducts()]
    for dep in DEPENDENCIES:
        if dep in installed_prods:
            qi.uninstallProducts((dep,))
        qi.installProduct(dep)
        transaction.savepoint()
        print >> out, "Installed dependency: %s" % dep

    context.getLogger("collective.collage.easyslider").info(out.getvalue())
    
    return out.getvalue()
