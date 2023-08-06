# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setuphandlers.py 273 2008-06-13 21:44:33Z flarumbe $
#
# end: Platecom header
""" CMFDefault setup handlers.

"""
from StringIO import StringIO

from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from zope.component import getUtility
from zope.app.component.hooks import setSite
from zope.app.component.interfaces import ISite, IPossibleSite
from Products.CMFCore.utils import getToolByName
from Products.Five.site.localsite import enableLocalSiteHook

import interfaces
from preferences import icCommunityManagementMailmanPersistence
from config import HAS_PLONE3

def setup_site(portal, out):
    """

        >>> from iccommunity.mailman import interfaces
        >>> from zope.app.component.hooks import setSite
        >>> setSite(portal)

        >>> sm = portal.getSiteManager()
        >>> utility = sm.queryUtility(interfaces.IicCommunityManagementMailman,
        ...                           name='iccommunity.configuration')
        >>> utility # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        <icCommunityManagementMailman at /plone.../>

    """
    sm = portal.getSiteManager()

    if not sm.queryUtility(interfaces.IicCommunityManagementMailman, name='iccommunity.configuration'):
        if HAS_PLONE3:
            sm.registerUtility(icCommunityManagementMailmanPersistence(),
                               interfaces.IicCommunityManagementMailman,
                               'iccommunity.configuration')
        else:
            sm.registerUtility(interfaces.IicCommunityManagementMailman,
                               icCommunityManagementMailmanPersistence(),
                               'iccommunity.configuration')

def importVarious(context):
  """ Import various settings.

  This provisional handler will be removed again as soon as full handlers
  are implemented for these steps.
  """
  site = context.getSite()
  out = StringIO()
  logger = context.getLogger("iccommunity.mailman")

  setup_site(site, out)

  print >> out, 'Various settings imported.'

  logger.info(out.getvalue())
  return out.getvalue()

def unimportVarious(context):
  """ Import various settings.

  This provisional handler will be removed again as soon as full handlers
  are implemented for these steps.
  """
  site = context.getSite()
  out = StringIO()
  logger = context.getLogger("iccommunity.core")

  print >> out, 'Various settings unimported.'

  logger.info(out.getvalue())
  return out.getvalue()
