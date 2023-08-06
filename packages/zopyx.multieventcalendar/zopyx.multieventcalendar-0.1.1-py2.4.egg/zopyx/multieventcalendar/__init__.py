
def initialize(context):
    """Initializer called when used as a Zope 2 product."""

# need for scripting
from Products.PythonScripts.Utility import allow_module
allow_module('calendar')
allow_module('logging')
allow_module('zLOG')
allow_module('md5')

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.FMLCustom.util').declarePublic('exportVCalendar')

