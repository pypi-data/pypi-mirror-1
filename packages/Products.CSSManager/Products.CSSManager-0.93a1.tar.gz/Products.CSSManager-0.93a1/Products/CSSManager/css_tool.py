from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
try:
  from celementtree import ElementTree
except:
  from elementtree import ElementTree

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFPlone.utils import safe_hasattr

import re

from config import ADD_CONTENT_PERMISSION,PROJECTNAME,view_permission,man_perm

fileWidgetName = 'cssmanager_widget_fileUploadRename'

def addcss_tool(self,REQUEST=None):
  """ Add a CSS Tool """
  st=css_tool()
  self._setObject("CSSManager_css",st)
    
class css_tool(UniqueObject,  SimpleItem):
  """ CSS Manager Tool """
  meta_type = "css_tool"
  id = "CSSManager_css"
  
  security = ClassSecurityInfo()
  configPage = PageTemplateFile('www/cssconfig', globals())
  
  manage_options = ({'label':'css configuration', 'action':'configPage'},) + SimpleItem.manage_options
  
  def __init__(self):
    """ css tool """
    self.id="CSSManager_css"
    self.propertiesFiles={'base_properties':'Base Properties'}


  security.declareProtected(man_perm, 'delFromMapping')
  def delFromMapping(self, key):
      """Remove a sheet from the mapping"""

      del self.propertiesFiles[key]
      self._p_changed = True


  security.declareProtected(man_perm, 'manage_delFromMapping')
  def manage_delFromMapping(self, REQUEST=None):
      """Form interface for removing selected sheets from the mapping"""

      if REQUEST is None:
          REQUEST = self.REQUEST

      for x in self.REQUEST.form.keys():
          if x.startswith("del_"):
              self.delFromMapping(x[4:])

      REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')


  def _getCurrentPropSheetName(self, REQUEST=None):
      """ a convenience method to get the
          name of the current property sheet """

      if REQUEST is None:
          REQUEST = self.REQUEST
      return REQUEST.form.get('chooser', 'base_properties')


  def _getBaseSkinFolder(self, propsFile):
      """ get the topmost path to a skin folder containing propsFile
      """
      
      propsFile = self._getCurrentPropSheetName()
      skinTool = getToolByName(self, 'portal_skins')
      skinName = skinTool.getDefaultSkin()
      skinObj = skinTool.getSkinByName(skinName)
      skinPath = skinObj.getPhysicalPath()
      currPath = None
      for path in skinPath:
          tmp = getattr(skinTool.getSkinByPath(path), propsFile, None)
          if tmp is not None:
              currPath = path
      if currPath is None:
          return None
      return getattr(skinTool, currPath)
      

  def redirectWithMessage(self, url, message, REQUEST=None):
      """ Redirect to a URL with a status message
      """
      
      if REQUEST is None:
          REQUEST = self.REQUEST
      utils = getToolByName(self, 'plone_utils')
      addPortalMessage = getattr(utils, 'addPortalMessage')
      if addPortalMessage is not None:
          utils.addPortalMessage(message, request=REQUEST)
          REQUEST.RESPONSE.redirect(url)
      else:
          if url.find('?') > 0:
              delim = '&'
          else:
              delim = '?'
          REQUEST.RESPONSE.redirect("%s%sportal_status_message=%s" % (url, delim, message))

  

  security.declareProtected(man_perm, 'getCurrentProps') 
  def getCurrentProps(self):
      """ get the topmost skin property object
      """

      propsFile = self._getCurrentPropSheetName()
      basePath = self._getBaseSkinFolder(propsFile)
      return basePath[propsFile]
  

  security.declareProtected(man_perm, 'isCustomized')
  def isCustomized(self):
      """ Have we already copied this to custom?
      """

      props = self.getCurrentProps()
      return getattr(props, 'manage_doCustomize', None) is None
  

  security.declareProtected(man_perm, 'makeCustomProps')
  def makeCustomProps(self):
    baseProps = self.getCurrentProps()
    baseProps.manage_doCustomize('custom')


  security.declareProtected(man_perm, 'getSelectedProperties')
  def getSelectedProperties(self):
    """ get property sheet """

    return self.getCurrentProps()
  

  security.declareProtected(man_perm, 'showChooser')
  def showChooser(self):
    
    if len(self.propertiesFiles) > 1:
      return True
    else:
      return False
  

  security.declareProtected(man_perm, 'parseHelpFile')
  def parseHelpFile(self):
      """ Return a help file matching the current
          property sheet as an ElementTree.
      """
    
      helpFile = '%s_help' % self._getCurrentPropSheetName()
      basePath = self._getBaseSkinFolder(helpFile)
      if basePath is None:
          return ElementTree()
      helpFile = getattr(basePath, helpFile)
      return ElementTree.fromstring(helpFile())


  security.declareProtected(man_perm, 'getAttrib')
  def getAttrib(self, element, attribute):
    return element.get(attribute)
  
  security.declareProtected(man_perm, 'getText')
  def getText(self, element):
    return element.text

  
  security.declareProtected(man_perm, 'get_cssname')
  def get_cssname(self,info):
      """ get the name of a css object """

      return self.propertiesFiles[info]

  
  security.declareProtected(man_perm, 'manage_addToMapping')
  def manage_addToMapping(self,key,val,REQUEST=None):
      """ add a property sheet to the editable list.
      """
  
      if getattr(self, key) is not None:
          self.propertiesFiles[key]=val
          self._p_changed = True
      
      if REQUEST is not None:
          REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')


  security.declareProtected(man_perm, 'customizeProps')
  def customizeProps(self, REQUEST=None):
      """ Copy skins property sheet to custom
      """
      
      if REQUEST is None:
          REQUEST = self.REQUEST
      self.makeCustomProps()
      REQUEST.RESPONSE.redirect('%s/prefs_cssmanager_form?chooser=%s' % 
       (self.portal_url(), self._getCurrentPropSheetName(REQUEST)))


  security.declareProtected(man_perm, 'enableDebugMode')
  def enableDebugMode(self, REQUEST=None):
    css_tool = getToolByName(self, 'portal_css')
    css_tool.setDebugMode(True)
    REQUEST.RESPONSE.redirect(self.portal_url()+"/prefs_cssmanager_form")

  security.declareProtected(man_perm, 'disableDebugMode')
  def disableDebugMode(self, REQUEST=None):
    css_tool = getToolByName(self, 'portal_css')
    css_tool.setDebugMode(False)
    REQUEST.RESPONSE.redirect(self.portal_url()+"/prefs_cssmanager_form")
    

  security.declareProtected(man_perm, 'setStyles')
  def setStyles(self, REQUEST=None):
      """ Update the prop sheet with new styles
      """
    
      if REQUEST is None:
          REQUEST = self.REQUEST

      portal_skins = getToolByName(self, 'portal_skins')
      chooser = self._getCurrentPropSheetName(REQUEST)
      css = getattr(self,chooser)
      props = self.parseHelpFile()
      
      # files need special treatment; we need to add
      # the image to custom
      for prop in props:
          if prop.get('widget') == fileWidgetName:
              propId = prop.get('id')
              input = REQUEST.form.get(propId)
              if input:
                  filename = input.filename
                  portal_skins.custom.manage_addImage(id=filename, file=input)
                  # put the filename in the REQUEST in place of the file
                  REQUEST.set(propId, filename)
              else:
                  # remove it from the request, or it will
                  # cause manage_changeProperties to try
                  # to pickle the file request object :P
                  del REQUEST.form[propId]

      css.manage_changeProperties(REQUEST)

      ms = self.translate(msgid="cssmanager_cssedited",domain="cssmanager")
      self.redirectWithMessage(
        "%s/prefs_cssmanager_form?chooser=%s" % (self.portal_url(), chooser),
        ms, REQUEST=REQUEST)


  security.declareProtected(man_perm, 'getmapping')
  def getmapping(self):
    """ raus """
    return self.propertiesFiles.items()
  
  security.declareProtected(view_permission, 'checkForColor')
  def checkForColor(self,color):
    """ Check if string is color """
    hexcolor = re.compile('#[0-9a-fA-F]{6}')
    nc =  ['black','white','red','purple','white','green','yellow','blue','grey','silver', 'grey', 'maroon', 'fuchsia', 'lime', 'olive', 'navy', 'teal', 'aqua']
    erg = 0
    try:
      check = hexcolor.search(color) or color.lower() in nc
      if check:
        erg = 1
      else:
        erg = 0
    except:
      erg = 0
    return erg
  
InitializeClass(css_tool)