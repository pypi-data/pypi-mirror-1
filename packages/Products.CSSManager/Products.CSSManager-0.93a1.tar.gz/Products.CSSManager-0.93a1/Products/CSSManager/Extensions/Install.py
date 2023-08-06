from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CSSManager.config import *
from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def install(self):
    out = StringIO()

    
    self.manage_addProduct["CSSManager"].manage_addTool(type="css_tool")
	
    try:
        from Products.CSSManager.config import DEPENDENCIES
    except:
        DEPENDENCIES = []
    portal = getToolByName(self,'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    for dependency in DEPENDENCIES:
        print >> out, "Installing dependency %s:" % dependency
        quickinstaller.installProduct(dependency)
        get_transaction().commit(1)
    install_subskin(self, out, GLOBALS)
    portal = getToolByName(self, 'portal_url').getPortalObject()
    portal.portal_controlpanel.registerConfiglet(**cssmanager_configlet)
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
    
def _skinsTool(self):
    return getToolByName(self, 'portal_skins')
    
def uninstall(self):
    out = StringIO()
    portal = getToolByName(self, 'portal_url').getPortalObject()
    
    try:
        self.portal_controlpanel.unregisterApplication(PROJECTNAME)
    except:
        pass
    
    print >>out, "Removing layers from portal_skins..."
    deleteLayers(_skinsTool(self), ['CSSManager'])
    return out.getvalue()
        
# below is taken from weblionLibrary. I didn't want plone people to have to install it if they only needed it for CSSManager
def deleteLayers(skinsTool, layersToDelete):
    """Remove each of the layers in `layersToDelete` from all skins.
    
    (We check them all, in case the user manually inserted it into some.)
    
    Pass getToolByName(portal, 'portal_skins') for `skinsTool`.
    
    """
    # Thanks to SteveM of PloneFormGen for a good example.
    for skinName in skinsTool.getSkinSelections():
        layers = [x.strip() for x in skinsTool.getSkinPath(skinName).split(',')]
        try:
            for curLayer in layersToDelete:
                layers.remove(curLayer)
        except ValueError:  # thrown if a layer ain't in there
            pass
        skinsTool.addSkinSelection(skinName, ','.join(layers))  # more like "set" than "add"
