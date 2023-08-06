from zope.component import getMultiAdapter
from zope.app.form.browser import ASCIIWidget
from zope.app.form.interfaces import ConversionError
from zope.app.form.browser.textwidgets import renderElement

from Acquisition import aq_inner

from quintagroup.plonecaptchas import ProductMessageFactory as _

class CaptchaWidget(ASCIIWidget):
    def __call__(self):
        captcha = getMultiAdapter((aq_inner(self.context.context), self.request), name='captcha')
        kwargs = {'type': self.type,
                  'name': self.name,
                  'id': self.name,
                  'cssClass': self.cssClass,
                  'style': self.style,
                  'size': self.displayWidth,
                  'extra': self.extra}
        if self.displayMaxWidth:
            kwargs['maxlength'] = self.displayMaxWidth # TODO This is untested.

        return u"""<div class="captchaImage">%s</div>%s""" % \
            (captcha.image_tag(), renderElement(self.tag, **kwargs))

    def _toFieldValue(self, input):
        # Verify the user input against the captcha
        captcha = getMultiAdapter((aq_inner(self.context.context), self.request), name='captcha')
        if not captcha.verify(input):
            raise ConversionError(_(u"Please re-enter validation code."))
        return super(CaptchaWidget, self)._toFieldValue(input)
