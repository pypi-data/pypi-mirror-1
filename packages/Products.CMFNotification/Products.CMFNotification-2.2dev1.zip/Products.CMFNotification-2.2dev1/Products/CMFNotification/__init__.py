"""Product initialization.

$Id: __init__.py 111706 2010-02-25 11:17:59Z jcbrand $
"""
from Products.CMFCore import utils as CMFCoreUtils
import Products.CMFNotification.patches

def initialize(context):
    import NotificationTool
    tools = (NotificationTool.NotificationTool, )
    CMFCoreUtils.ToolInit(NotificationTool.META_TYPE,
                          tools=tools,
                          icon='tool.gif').initialize(context)
