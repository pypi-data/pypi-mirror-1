Plone Captchas
==============

quintagroup.plonecaptchas is a simple captchas implementation for Plone, designed
for validation of human input in insecure forms. This is a standalone 
implementation with static captcha images, which does not depend on captchas.net 
services.

quintagroup.plonecaptchas has dynamic captchas option implemented. You can
switch captchas into dynamic mode in the correspondent configlet. In this
case, captcha images will be generated on the fly.

Requirements
------------

* Plone 3.0 and above 

For earlier Plone versions - use 1.3.4 version of qPloneCaptchas product for use on forms
created with PloneFormMailer product.

Dependency
----------

PIL with Jpeg and FreeType support

Plone Captchas plugs to
-----------------------

* default Plone discussion mechanism

* join form

* send_to form

* forms created with PloneFormGen

Plone Captchas on PloneFormGen forms 
------------------------------------

To make captchas work on forms created with PloneFormGen, please use qPloneCaptchaField product:

* Plone Captcha Field home page - http://quintagroup.com/services/plone-development/products/plone-captcha-field

* Instruction on use - http://projects.quintagroup.com/products/wiki/qPloneCaptchaField
  
* Plone Captcha Field Screencast - http://quintagroup.com/cms/screencasts/qplonecaptchafield

Installation
------------

See docs/INSTALL.txt for instructions.

Authors
-------

The product was developed by Quintagroup team:

* Volodymyr Cherepanyak

* Mykola Kharechko

* Vitaliy Stepanov

* Bohdan Koval

Contributors
------------

* Dorneles Tremea

Future features
---------------

* Configuration of captchas images generation (shade, background, colors etc.)

Links
-----

* Plone Captchas home page - http://quintagroup.com/services/plone-development/products/plone-captchas

* Plone Captchas Screencasts - http://quintagroup.com/cms/screencasts/qplonecaptchas
