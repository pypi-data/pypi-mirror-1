# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: interfaces.py 301 2008-06-19 18:57:23Z crocha $
#
# end: Platecom header
""" iccommunity.mailman interfaces.
"""
# pylint: disable-msg=W0232,R0903

from zope import schema
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from iccommunity.mailman.i18n import _

class IicCommunitySite(Interface):
	"""
	"""

class IicCommunityManagementMailman( Interface ):
	"""
	"""
	host = schema.ASCIILine(title = _(u"URI"),
						   required = False,
						   description = _(u"Host of the LDAP server with mailman entry (ldap://ldap.host.com/),"
							   u"or files where mailman exists (file:///usr/lib/mailman)."),
						   )
	available_lists = schema.List(title = _(u"Available Lists"),
								  required = False,
								  default = [],
								  description = _(u"Available Lists"),
								  value_type=schema.Choice(vocabulary="iccommunity.mailman.lists"))

class IicCommunityMailmanUserLists( Interface ):
	"""
	"""
	subscribed_lists = schema.List(title = _(u"Subscribed Lists"),
								   required = False,
								   default = [],
								   description = _(u"Subscribed Lists"),
								   value_type=schema.Choice(vocabulary="iccommunity.mailman.available_lists"))

class IicCommunityMailman( Interface ):
	"""
	"""

	def get_lists(self):
		"""
		Retorna las listas del mailman.

			@rtype: list
			@return: Listas del mailman.
		"""

	def get_members(self, listname):
		"""
		Retorna los miembros de una lista

			@listname: List name
			@return: List of members
		"""
	def get_listbyGroups(self, groups):
		"""
		Retorna las listas del mailman asociadas a cada grupo.

			@type groups: list
			@param groups: La lista de grupos.

			@rtype: list
			@return: Listas del mailman asociadas a cada grupo.
		"""

	def set_listbyGroups(self, groups, lists):
		"""
		Define las listas de un grupo.

			@type groups: list
			@param groups: La lista de grupos.
			@type lists: list
			@param lists: Las listas.

			@rtype: None
		"""

	def set_host(self, host):
		"""
		Setea el origen del mailman. host puede ser None (Usar el mailman local) o un PloneLdap?.

			@type host: object
			@param host: Host del mailman.

			@rtype: None
		"""

	def subscribed_lists(self, member):
		"""
		Return lists where member is subscribed

			@member: Plone member
			@return: List of mailman lists
		"""

	def subscribe(self, member, listname, password=None, digest = False,
			ack = 0, admin_notif = 0, text=None, whence='icCommunity.mailman' ):
		"""
		Inscribe un miembro a una lista.

			@member: Plone member
			@listname: Mailman list name
			@password: Password for mailman administration. None mean random password.
			@digest: Accept digest mail
			@ack: flag specifies user should get an acknowledgement of subscription.
			@admin_notif: flag specifies admin notify.
			@text: text to append to ack
			@whence: from the modification was made.

			@return: Listas del mailman.
		"""

	def unsubscribe(self, member, listname, admin_notif=0, ack=0, whence='icCommunity.mailman'):
		"""
		Desuscribe un miembro a una lista.

			@member: Plone member
			@listname: Mailman list name
			@password: Password for mailman administration. None mean random password.
			@digest: Accept digest mail
			@ack: flag specifies user should get an acknowledgement of subscription.
			@admin_notif: flag specifies admin notify.
			@text: text to append to ack
			@whence: from the modification was made.

			@return: Listas del mailman.
		"""

