# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: vocabularies.py 326 2008-07-15 18:09:25Z crocha $
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

from icsemantic.core.i18n import _
from icsemantic.core.config import HAS_PLONE3

import cgi

if HAS_PLONE3:
	from plone.i18n.locales.interfaces import IContentLanguageAvailability
else:
	from Products.PloneLanguageTool import availablelanguages

class ContentTypesVocabulary(object):
	"""

	Test ContentTypes vocab,

		>>> from icsemantic.core.vocabularies import ContentTypesVocabularyFactory
		>>> ccvocab = ContentTypesVocabularyFactory(portal)
		>>> ccvocab
		<zope.schema.vocabulary.SimpleVocabulary object at ...>
		>>> [term.title for term in ccvocab] # doctest: +ELLIPSIS
		...											 +NORMALIZE_WHITESPACE
		[...u'Event', u'Favorite', u'File', u'Folder', u'Image',
		u'Large Folder', u'Link', u'News Item', u'Page'...]

	"""
	implements(IVocabularyFactory)

	def __call__(self, context):
		context = getattr(context, 'context', context)
		portal_types = getToolByName(context, 'portal_types')
		properties = getToolByName(context, 'portal_properties')
		terms = []
#		import pdb;pdb.set_trace()
		types = filter( lambda x: x.global_allow, portal_types.objectValues() )
		types_not_searched = set( properties.site_properties.types_not_searched )

		for type in portal_types.objectValues():
			if type.getId() not in types_not_searched:
				terms.append(vocabulary.SimpleTerm(unicode(type.content_meta_type),
												   title=unicode(type.title_or_id())))

		terms.sort( lambda x,y: cmp( x.title, y.title ) )

		return vocabulary.SimpleVocabulary( terms )

ContentTypesVocabularyFactory = ContentTypesVocabulary()

from Products.CMFPlone.utils import safe_unicode

# Este vocabulario se reemplaza por icsemantic.availablelanguages de icsemantic.fallback
class LanguagesVocabulary(object):
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

        portal_languages = getToolByName(context, 'portal_languages')
        terms = portal_languages.listSupportedLanguages()

        return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(term[0], title=safe_unicode(term[1])) \
                                            for term in terms])

LanguagesVocabularyFactory = LanguagesVocabulary()

if HAS_PLONE3:
	availablelanguages = queryUtility(IContentLanguageAvailability)

