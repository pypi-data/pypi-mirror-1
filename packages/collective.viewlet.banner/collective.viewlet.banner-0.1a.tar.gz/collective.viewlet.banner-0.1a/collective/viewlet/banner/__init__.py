
from Products.CMFCore import utils 

import banner_tool

# group the tool
tools = ( banner_tool.BannerTool,
          )


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    utils.ToolInit(
        'Banner Tool', tools=tools,
        icon='tool.gif',
        ).initialize(context)
