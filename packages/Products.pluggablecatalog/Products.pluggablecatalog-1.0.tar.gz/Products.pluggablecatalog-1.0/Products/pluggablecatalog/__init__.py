from Products.CMFCore.utils import ToolInit

from Products.pluggablecatalog import tool
from Products.pluggablecatalog import config


def initialize(context):
    ToolInit(config.PROJECTNAME+ ' Tool',
             tools = (tool.CatalogTool, ),
             icon='tool.gif',
             ).initialize(context)

