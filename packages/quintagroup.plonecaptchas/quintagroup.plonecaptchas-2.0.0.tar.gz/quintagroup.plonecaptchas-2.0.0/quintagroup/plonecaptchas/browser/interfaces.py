from zope.interface import Interface
from zope.schema.interfaces import IASCIILine

class ICaptchaView(Interface):
    """ Captcha generating and verifying view that is wrapper around
        captcha generation scripts located in skins folder.

        Use the view from a page to generate an image tag ('image_tag' method) 
        and to verify user input ('verify' method).
    """

    def image_tag():
        """Generate an image tag linking to a captcha"""

    def verify(input):
        """ Verify user input.
        """

class ICaptcha(IASCIILine):
    u"""A field for captcha validation"""
