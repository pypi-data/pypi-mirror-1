# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: vocabularies.py 316 2008-06-27 19:05:40Z jpgimenez $
#
# end: Platecom header
"""
"""
from zope.schema import vocabulary
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.component import getUtility
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IPropertiesTool

from iccommunity.core.i18n import _
from iccommunity.core.config import HAS_PLONE3

if HAS_PLONE3:
	from plone.i18n.locales.interfaces import IContentLanguageAvailability
else:
	from Products.PloneLanguageTool import availablelanguages

from iccommunity.mailman.interfaces import IicCommunityManagementMailman, IicCommunityMailman

class MailmanploneListsVocabulary(object):
	"""

	Test ContentTypes vocab,

		>>> from iccommunity.mailman.vocabularies import MailmanploneListsVocabulary
		>>> vocab = MailmanploneListsVocabulary(portal)
		>>> vocab
		<zope.schema.vocabulary.SimpleVocabulary object at ...>

	"""
	implements(IVocabularyFactory)

	def __call__(self, context):
		context = getattr(context, 'context', context)
		terms = []
		pcm = getUtility(IicCommunityManagementMailman,
						 name='iccommunity.configuration')
		if pcm.host:
			util=queryUtility(IicCommunityMailman)
			util.set_host(pcm.host)
			terms = util.get_lists()

		return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(term) for term in terms])

MailmanploneListsVocabularyFactory = MailmanploneListsVocabulary()

class MailmanploneAvailableListsVocabulary(object):
	"""

	Test ContentTypes vocab,

		>>> from iccommunity.mailman.vocabularies import MailmanploneListsVocabulary
		>>> vocab = MailmanploneListsVocabulary(portal)
		>>> vocab
		<zope.schema.vocabulary.SimpleVocabulary object at ...>

	"""
	implements(IVocabularyFactory)

	def __call__(self, context):
		context = getattr(context, 'context', context)
		terms = []
		pcm = getUtility(IicCommunityManagementMailman,
						 name='iccommunity.configuration')
		if pcm.available_lists:
			terms = pcm.available_lists

		return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(term) for term in terms])

MailmanploneAvailableListsVocabularyFactory = MailmanploneAvailableListsVocabulary()
