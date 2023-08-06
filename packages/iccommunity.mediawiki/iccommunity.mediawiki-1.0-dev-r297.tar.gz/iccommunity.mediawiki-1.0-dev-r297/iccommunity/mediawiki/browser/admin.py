# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: admin.py 297 2008-06-18 20:11:11Z crocha $
#
# end: Platecom header
"""Forms
"""
from string import strip
from datetime import datetime
from zope import event
from Acquisition import aq_inner

#from zope.app.form import CustomWidgetFactory
#from zope.app.form.browser import ObjectWidget
#from Products.Five.form.objectwidget import ObjectWidget
#from zope.app.form.browser import ListSequenceWidget

from zope.app.component.hooks import getSite
from zope.formlib import form

try:
	from zope.lifecycleevent import ObjectModifiedEvent
except:
	from zope.app.event.objectevent import ObjectModifiedEvent

from icsemantic.core.browser.base import BaseSettingsForm

from Products.Five.formlib import formbase
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from iccommunity.mediawiki import interfaces
from iccommunity.mediawiki import MediawikiMessageFactory as _

# This is not working on Plone 2.5, but I don't know why. It would be
# better to have this instead of the current implementation.
#from iccommunity.mediawiki.preferences import RolesPair
#rolespair_widget = CustomWidgetFactory(ObjectWidget, RolesPair)
#rolemap_widget = CustomWidgetFactory(ListSequenceWidget,
									 #subwidget=rolespair_widget)


class MediawikiRolesMapper(BaseSettingsForm):
	"""Configlet to map Plone roles to mediawiki roles"""
	form_name = _(u'Mediawiki Roles Mapper')
	form_fields = form.Fields(interfaces.IicCommunityManagementMediawikiRolesMapper,
							  render_context=True)
	#form_fields['rolemap'].custom_widget = rolemap_widget

	@form.action(_("Apply"), condition=form.haveInputWidgets)
	def handle_edit_action(self, action, data):
		rolemap = data['rolemap']
		mtool = getToolByName(aq_inner(self.context), 'portal_membership')
		plone_roles = mtool.getPortalRoles()
		#TODO: integrate with the Mediawiki utility
		mediawiki_roles = ['sysop']

		#XXX: move this to a validator?
		for item in rolemap:
			if item is None:
				continue

			if item.find(';') < 0:
				message = _('No ";" found.'
							'The items must match the following pattern: '
							'"Plone role; Mediawiki Role" without quotes. '
						   )
				IStatusMessage(self.request).addStatusMessage(message,
															  type=u'warn')
				return

			plone_role, mediawiki_role = tuple(map(strip, item.split(';')))
			if plone_role not in plone_roles:
				message = _('You entered a non valid Plone role. The items '
							'must match the following pattern: "Plone '
							'role; Mediawiki Role" without quotes, where '
							'Plone role is a valid role in the portal. '
							'Valid Plone roles are: %s' % (plone_roles,))
				IStatusMessage(self.request).addStatusMessage(message,
															  type=u'warn')
				return
			elif mediawiki_role not in mediawiki_roles:
				message = _('You entered a non valid Mediawiki role. The '
							'items must match the following pattern: '
							'"Plone role; Mediawiki Role" without quotes, '
							'where Plone role is a valid role in the '
							'portal. Valid Mediawiki roles are: %s' %
							(mediawiki_roles,))
				IStatusMessage(self.request).addStatusMessage(message,
															  type=u'warn')
				return

		if form.applyChanges(self.context, self.form_fields, data,
							 self.adapters):
			event.notify(ObjectModifiedEvent(self.context))
			self.status = _("Updated on ${date_time}",
				mapping={'date_time': str(datetime.utcnow())}
				)
		else:
			self.status = _('No changes')


class MediawikiSQLServer(BaseSettingsForm):
	"""Configlet for the Mediawiki SQL Server"""
	form_name = _(u'Mediawiki SQL Server')
	form_fields = form.Fields(interfaces.IicCommunityManagementMediawikiSQLServer,
							  render_context=True)

	@form.action(_("Apply"), condition=form.haveInputWidgets)
	def handle_edit_action(self, action, data):
		if form.applyChanges(self.context, self.form_fields, data,
							 self.adapters):
			# Connect to the SQL server to check parameters.
			import _mysql
			from _mysql_exceptions import ProgrammingError, OperationalError, DatabaseError
			try:
				db = _mysql.connect(host=data["hostname"],
					user=data["username"],
					passwd=data["password"],
					db=data["database"])
				if not data['dbprefix']: data['dbprefix'] = ""
				db.query("SELECT * from %suser" % data['dbprefix'])
				r = db.store_result()
				# Ok.
				event.notify(ObjectModifiedEvent(self.context))
				self.status = _("Updated on ${date_time}",
					mapping={'date_time': str(datetime.utcnow())}
					)
			except ( ProgrammingError, OperationalError ), m:
				code, mess = m
				self.status = _('Error ${code}: ${msg}', mapping={'code': code, 'msg': mess})
		else:
			self.status = _('No changes')

