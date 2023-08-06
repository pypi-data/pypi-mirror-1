# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: preferences.py 280 2008-06-16 12:50:28Z crocha $
#
# end: Platecom header
from zope.interface import implements
from zope.component import getUtility
from OFS.SimpleItem import SimpleItem
from zope.schema.fieldproperty import FieldProperty
from icsemantic.core.annotations import KeywordBasedAnnotations
from fieldproperty import ToolDependentFieldProperty, AuthenticatedMemberFieldProperty

import interfaces

class icSemanticManagementContentTypes(SimpleItem):
    implements(interfaces.IicSemanticManagementContentTypes)

    def __call__(self):
        import pdb;pdb.set_trace()

    fallback_types = ToolDependentFieldProperty(interfaces.IicSemanticManagementContentTypes['fallback_types'])

def content_types_form_adapter(context):
    pcm = getUtility(interfaces.IicSemanticManagementContentTypes,
                     name='icsemantic.configuration',
                     context=context)
    return pcm

class icSemanticManagementUserLanguagesFactory(KeywordBasedAnnotations):
    implements(interfaces.IicSemanticManageUserLanguages)

    icsemantic_preferred_languages = AuthenticatedMemberFieldProperty(interfaces.IicSemanticManageUserLanguages['icsemantic_preferred_languages'], 'icsemantic.preferred_languages')

