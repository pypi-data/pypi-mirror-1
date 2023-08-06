# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 280 2008-06-16 12:50:28Z crocha $
#
# end: Platecom header
try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

import icsemantic.core
PACKAGE = icsemantic.core

PROJECTNAME = "icsemantic.core"
PACKAGENAME = "icsemantic.core"

DEPENDENCIES = []

from Products.CMFCore.permissions import SetOwnProperties

CONFIGLETS = ()
GLOBALS = globals()
