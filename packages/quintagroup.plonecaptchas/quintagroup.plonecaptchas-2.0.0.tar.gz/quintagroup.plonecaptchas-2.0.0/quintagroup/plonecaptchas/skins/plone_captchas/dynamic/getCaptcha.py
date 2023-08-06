## Script (Python) "getCaptcha"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
from quintagroup.plonecaptchas.utils import getCaptchasCount, formKey, encrypt

from random import randint
key = formKey(randint(0, getCaptchasCount(True)))
encrypted_key = encrypt(context.captcha_key, key)

return encrypted_key
