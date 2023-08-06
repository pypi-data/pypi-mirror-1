## Script (Python) "validate_captcha"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters= captcha=''
##title=Validates content publishing
##

from Products.CMFPlone import PloneMessageFactory as _

captcha_valid = context.restrictedTraverse('@@captcha').verify(captcha)

if not captcha_valid:
	state.setError('captcha', _(u'This field is required, please provide some information.'), 'captcha_missing')

if state.getErrors():
	context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
	return state.set(status='failure')
else:
	return state

