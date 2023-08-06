from Products.CMFCore.utils import getToolByName

from config import *

def setupVarious(context):
    tt = getToolByName(context.getSite(), TOOL_ID, None)
    if tt is None:
        addTool = context.getSite().manage_addProduct[PRODUCTNAME].manage_addTool
        addTool(TOOLTYPE)
