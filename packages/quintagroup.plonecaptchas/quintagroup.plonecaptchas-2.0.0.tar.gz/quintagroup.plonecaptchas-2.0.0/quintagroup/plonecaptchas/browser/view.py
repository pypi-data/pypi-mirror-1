from DateTime import DateTime

from zope.interface import implements

from Acquisition import aq_parent
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from quintagroup.plonecaptchas.browser.interfaces import ICaptchaView
from quintagroup.plonecaptchas.utils import decrypt, parseKey, encrypt1, getWord

COOKIE_ID = 'captchahashkey'

class Captcha(BrowserView):
    implements(ICaptchaView)

    def getSafeContext(self):
        """ Return context for this view that is acquisition aware (it's needed
            because when this view is called from captcha widget self.context 
            may be some adapted object and it isn't aqcuisiton wrapped).
        """
        if aq_parent(self.context) is not None:
            return self.context
        else:
            return self.context.context

    def image_tag(self):
        """ Generate an image tag linking to a captcha """
        context = self.getSafeContext()
        hk = context.getCaptcha()
        resp = self.request.response
        if COOKIE_ID in resp.cookies:
            # clear the cookie first, clearing out any expiration cookie
            # that may have been set during verification
            del resp.cookies[COOKIE_ID]
        resp.setCookie(COOKIE_ID, hk, path='/')
        portal_url = getToolByName(context, 'portal_url')()
        img_url = '%s/getCaptchaImage/%s' % (portal_url, hk)
        return '<img src="%s" />' % img_url

    def verify(self, input):
        context = self.getSafeContext()
        result = False
        try:
            hashkey = self.request[COOKIE_ID]
            self.request.response.expireCookie(COOKIE_ID, path='/')

            decrypted_key = decrypt(context.captcha_key, hashkey)
            parsed_key = parseKey(decrypted_key)
            index = parsed_key['key']
            date = parsed_key['date']

            captcha_type = context.getCaptchaType()
            if captcha_type == 'static':
                img = getattr(context, '%s.jpg' % index)
                solution = img.title
                enc = encrypt1(input)
            else:
                enc = input
                solution = getWord(int(index))

            captcha_tool = getToolByName(context, 'portal_captchas')
            if (enc != solution) or (captcha_tool.has_key(decrypted_key)) or (DateTime().timeTime() - float(date) > 3600):
                pass
            else:
                captcha_tool.addExpiredKey(decrypted_key)
                result = True
        except KeyError:
            pass # No cookie

        return result
