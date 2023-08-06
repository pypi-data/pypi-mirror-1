from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import css_tool
from config import *

def initialize(context):
	registerDirectory('skins', globals())
	utils.ToolInit(
     	   PROJECTNAME + ' Tools'
     	   , tools = (css_tool.css_tool,)
    	    # , product_name = PROJECTNAME
    	    , icon='css_manager_logo.gif'
   	     ).initialize(context)
