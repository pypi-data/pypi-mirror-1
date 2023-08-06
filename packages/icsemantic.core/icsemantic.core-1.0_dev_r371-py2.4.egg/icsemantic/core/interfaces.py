# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: interfaces.py 326 2008-07-15 18:09:25Z crocha $
#
# end: Platecom header
""" icsemantic.core interfaces.
"""
# pylint: disable-msg=W0232,R0903

from zope import schema
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty
from icsemantic.core.i18n import _

class IicSemanticSite(Interface):
    """ represents a platecom installation, should be a local site
        with local components installed
    """

class IicSemanticConfiglet(Interface):
    """ platecom configlet
    """

class IicSemanticManagementContentTypes( Interface ):

    fallback_types = schema.List(title = _(u"Fallback Content Types"),
                                 required = False,
                                 default = [],
                                 description = _(u"Content Types with language fallback capabilities"),
                                 value_type=schema.Choice(vocabulary="icsemantic.content_types"))

class IicSemanticUserConfiguration( Interface ):

    pref_languages = schema.List(title = _(u"Extra Language Configuration"),
                                 required = False,
                                 default = [],
                                 description = _(u"Alternative Languages"),
                                 value_type=schema.Choice(vocabulary="languages"))

class ILanguagesManager(Interface):
    """

    """
    def listCurrentUserLanguages(self):
        """
        """

    def listUserLanguages(self, user_id):
        """
        """

    def storeUserLanguages(self, user_id, languages):
        """
        """

class IMultilingualContentMarker(Interface):
    """ Marker para un ContentType que tiene
        getters multilingües
    """

class IMultilingualGettersMarker(Interface):
    """ Marker para un ContentType que tiene
        getters multilingües en lugar de los
        originales de archetypes
    """

class IContentTypesMultilingualPatcher(Interface):
    """ Utility para aplicar los parches de soporte multilenguaje
        a un ContentType en particular
    """
    def patch(self, klass):
        """ Incorpora los metodos con fallback multilingüe
        """

    def unpatch(self, klass):
        """ Remueve los metodos con fallback multilingüe
        """

class IFieldEmptiness( Interface ):
    """ Emptiness adapter.
    """

    def __call__(self, instance):
        """
        """

class IicSemanticManageUserLanguages( Interface ):
	"""
	"""
	icsemantic_preferred_languages = schema.List(title = _(u"User Languages"),
		required = False,
		default = [],
		description = _(u"User Languages"),
		value_type=schema.Choice(vocabulary="icsemantic.languages"))

