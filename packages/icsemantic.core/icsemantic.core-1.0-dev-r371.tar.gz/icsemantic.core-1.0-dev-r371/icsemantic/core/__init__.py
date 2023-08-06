# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: __init__.py 313 2008-06-26 21:09:08Z flarumbe $
#
# end: Platecom header
import os, sys
from Globals import package_home
from Products.CMFCore.DirectoryView import registerDirectory

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

pkg_home = package_home( globals() )
lib_path = os.path.join( pkg_home, 'lib' )

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
