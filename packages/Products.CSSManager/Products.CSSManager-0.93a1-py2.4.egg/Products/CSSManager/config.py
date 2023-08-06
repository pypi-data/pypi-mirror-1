from Products.CMFCore.permissions import AddPortalContent,View,ManagePortal
from Products.Archetypes.public import DisplayList

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "CSSManager"
SKINS_DIR = 'skins'
view_permission = View
man_perm = ManagePortal
GLOBALS = globals()


DEPENDENCIES = []
cssmanager_configlet = {
    'id': 'css_manager',
    'appId': 'CSSManager',
    'name': 'Theme Configuration Manager',
    'action': 'string:$portal_url/prefs_cssmanager_form',
    'category': 'Products',
    'permission': (ManagePortal,),
    'imageUrl': 'css_manager_logo.gif',
    }
