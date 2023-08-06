from AccessControl import allow_module, allow_class
from collective.captcha.browser.captcha import Captcha

def initialize(context):
	"""Initializer called when used as a Zope 2 product."""

	allow_module('collective.captcha.browser.captcha')
	allow_class(Captcha)
