# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: admin.py 299 2008-06-19 16:55:47Z crocha $
#
# end: Platecom header
"""
admin setting and preferences
Solo vistas y forms

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

import os
from datetime import datetime

import zope
from zope import component
from zope.component import getUtility
from zope.formlib import form

try:
	from zope.lifecycleevent import ObjectModifiedEvent
except:
	from zope.app.event.objectevent import ObjectModifiedEvent

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser import BrowserView
from Products.Five.formlib import formbase

from icsemantic.core.i18n import _
from icsemantic.core.browser.base import BaseSettingsForm
from icsemantic.catalog import interfaces

class AdvancedSearchOptions(BaseSettingsForm):
	"""Configlet to set advanced search options"""

	form_name = _(u'Advanced Search Options')
	form_fields = form.Fields(interfaces.IicSemanticManagementAdvancedSearchOptions)

	@form.action(_("Apply"), condition=form.haveInputWidgets)
	def handle_edit_action(self, action, data):
		if form.applyChanges(self.context, self.form_fields, data,
							 self.adapters):
			zope.event.notify(ObjectModifiedEvent(self.context))
			self.status = _("Updated on ${date_time}",
				mapping={'date_time': str(datetime.utcnow())}
				)
		else:
			self.status = _('No changes')

