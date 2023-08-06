
try:
    from Products.AdvancedQuery import AdvancedQuery
except: raise Exception, "You have to install AdvancedQuery!"

from Products.CMFCore.utils import ToolInit

import QueryTool
from config import *

import patches

def initialize(context):
    ToolInit(TOOL_ID, 
             tools=(QueryTool.QueryTool,),
             icon='tool.gif',
             ).initialize( context )

