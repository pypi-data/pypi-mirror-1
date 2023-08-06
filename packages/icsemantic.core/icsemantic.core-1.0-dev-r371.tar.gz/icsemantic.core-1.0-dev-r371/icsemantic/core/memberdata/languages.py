# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: languages.py 280 2008-06-16 12:50:28Z crocha $
#
# end: Platecom header
"""
Adapters y Utilities para el manejo de multi lenguajes

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

from AccessControl import getSecurityManager
from zope.interface import implements
from zope.i18n.interfaces import IUserPreferredLanguages

class icSemanticPropertyPreferredLanguages(object):
    """
    icsemantic.preferred_languages property utility
    """
    implements(IUserPreferredLanguages)

    def getPreferredLanguages(self, user=None):
        if not user:
            self.user = getSecurityManager().getUser()
        try:
            psheet = self.user.getPropertysheet('mutable_properties')
            return list(psheet.getProperty('icsemantic.preferred_languages'))
        except:
            return []

authenticated_member_icsemantic_languages_property = icSemanticPropertyPreferredLanguages()
member_icsemantic_languages_property = icSemanticPropertyPreferredLanguages()

class PlonePreferredLanguage(object):
    """
    icsemantic.preferred_languages property utility
    """
    implements(IUserPreferredLanguages)

    def getPreferredLanguages(self, user=None):
        if not user:
            self.user = getSecurityManager().getUser()
        try:
            psheet = self.user.getPropertysheet('mutable_properties')
            language = psheet.getProperty('language')
            if language:
                return [language,]
        except:
            pass
        return []

authenticated_member_plone_preferred_languages = PlonePreferredLanguage()
member_plone_preferred_languages = PlonePreferredLanguage()

