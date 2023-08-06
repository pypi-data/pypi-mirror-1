## Script (Python) "getCaptchaType"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=actions=None
##title=
##
from Products.CMFCore.utils import getToolByName
import string
skinsTool = getToolByName(context, 'portal_skins')
default_skin = skinsTool.getDefaultSkin()
path = skinsTool.getSkinPath(default_skin)
path = map( string.strip, string.split( path,',' ) )

if 'plone_captchas/static' in path:
    return 'static'
elif 'plone_captchas/dynamic' in path:
    return 'dynamic'
else:
    return None