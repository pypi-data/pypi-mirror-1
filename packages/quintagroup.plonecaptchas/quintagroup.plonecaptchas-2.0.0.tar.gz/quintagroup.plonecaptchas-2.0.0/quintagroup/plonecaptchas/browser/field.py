from zope.interface import implements
from zope.schema import ASCIILine
from quintagroup.plonecaptchas.browser.interfaces import ICaptcha

class Captcha(ASCIILine):
    implements(ICaptcha)
