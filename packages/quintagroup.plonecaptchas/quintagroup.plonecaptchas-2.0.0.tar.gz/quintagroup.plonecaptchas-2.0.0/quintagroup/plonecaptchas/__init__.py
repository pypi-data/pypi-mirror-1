from zope.i18nmessageid import MessageFactory

from AccessControl import allow_module, ModuleSecurityInfo
from Products.CMFCore.utils import ToolInit

from quintagroup.plonecaptchas import config
from quintagroup.plonecaptchas import CaptchaTool

ProductMessageFactory = MessageFactory('quintagroup.plonecaptchas')
ModuleSecurityInfo('quintagroup.plonecaptchas').declarePublic("ProductMessageFactory")

allow_module('quintagroup.plonecaptchas.utils')
allow_module('quintagroup.plonecaptchas.config')

def initialize(context):
    ToolInit(meta_type="CaptchaTool",
             tools=(CaptchaTool.CaptchaTool, ),
             icon=config.TOOL_ICON,).initialize(context)
