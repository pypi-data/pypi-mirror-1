# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: languages.py 280 2008-06-16 12:50:28Z crocha $
#
# end: Platecom header
""" icsemantic.core languages.
"""
# pylint: disable-msg=W0232,R0903

from zope.component import queryUtility
from zope.interface import implements
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

from interfaces import ILanguagesManager

class RequestPreferredLanguage(object):
    """
    icsemantic.preferred_languages property utility
    """
    implements(IUserPreferredLanguages)

    def __init__(self, context):
        self.context = context

    def getPreferredLanguages(self):
        if not hasattr(self.context, 'set_language'):
            return []

        return self.context.set_language

def request_preferred_languages(context):
    return RequestPreferredLanguage(context)

class icSemanticPreferredLanguage(object):
    """
    icsemantic.preferred_languages property utility
    """
    implements(IUserPreferredLanguages)

    utilities = ['authenticated_member_plone_preferred_languages',
                 'authenticated_member_icsemantic_languages_property',]

    def getPreferredLanguages(self, portal=None, request=None):
        languages = []
        # TODO: mover estos a un adapter
        if request and request.has_key('set_language'):
            languages += [request['set_language']]
        for utility in self.utilities:
            lang_util = queryUtility(IUserPreferredLanguages,
                                     name=utility)
            languages += [n for n in lang_util.getPreferredLanguages() \
                          if n not in languages]

        try:
            languages += [n for n in IUserPreferredLanguages(request).getPreferredLanguages() \
                          if n not in languages]
        except:
            pass
        if not portal:
            portal = getSite()
        if portal:
            portal_properties = getToolByName(portal, 'portal_properties')
            site_language = getattr(portal_properties.site_properties,
                                    'default_language', None)
            icsemantic_site_languages = getattr(portal_properties.site_properties,
                                              'icsemantic.languages', None)
            if site_language and site_language not in languages:
                languages += [site_language]
            if icsemantic_site_languages:
                languages += [n for n in icsemantic_site_languages \
                              if n not in languages]

        return languages

class LanguagesManager(object):
    """
    TODO: WCD 205
    """
    implements( ILanguagesManager )

    def listCurrentUserLanguages(self):
        """
        """

    def listUserLanguages(self, user_id):
        """
        """

    def storeUserLanguages(self, user_id, languages):
        """
        """
