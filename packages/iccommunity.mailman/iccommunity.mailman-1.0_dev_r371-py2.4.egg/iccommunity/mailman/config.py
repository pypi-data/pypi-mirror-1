# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 244 2008-06-11 19:45:48Z crocha $
#
# end: Platecom header
try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

import iccommunity.mailman
PACKAGE = iccommunity.mailman

PROJECTNAME = "iccommunity.mailman"
PACKAGENAME = "iccommunity.mailman"

DEPENDENCIES = ['iccommunity.core', ]

GLOBALS = globals()
