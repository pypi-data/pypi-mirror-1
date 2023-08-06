from Products.Clouseau.config import *
from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory('skins/Clouseau', product_globals)

try:
    import transaction
except ImportError:
    print "You must have Zope 2.9 for this library to work."
    raise

from Products.CMFCore import utils
from Products.Clouseau.tools.clouseautool import ClouseauTool
import permissions

tools = ( ClouseauTool, )

def initialize(context):
    utils.ToolInit(
		product_name,
		tools=tools,
        icon='clouseau.jpg').initialize(context)
