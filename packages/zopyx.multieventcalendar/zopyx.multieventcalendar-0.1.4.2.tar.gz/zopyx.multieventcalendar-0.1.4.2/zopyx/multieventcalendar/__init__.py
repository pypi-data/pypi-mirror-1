################################################################
# zopyx.multieventcalendar
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################


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

