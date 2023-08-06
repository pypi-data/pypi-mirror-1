# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: multilingual.py 254 2008-06-12 14:51:51Z crocha $
#
# end: Platecom header
"""
Utilities, adapters, markers... de todo un poco para
soportar contenido multi-lenguaje

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

import sys
from types import FunctionType as function

from zope.interface import implements, implementedBy, \
                           classProvides
from zope.app.component.hooks import getSite
from zope.component.interfaces import IFactory
from zope.component import queryUtility
from zope.i18n.interfaces import IUserPreferredLanguages

from Products.Archetypes.utils import capitalize
from Products.ATContentTypes.interfaces import IATContentType
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import classImplements, \
                                    classDoesNotImplement

from icsemantic.core.interfaces import IContentTypesMultilingualPatcher, \
                                      IMultilingualContentMarker, \
                                      IMultilingualGettersMarker, \
                                      IFieldEmptiness

NOT_FALLBACK_FIELDS = ['id',
                       'language',]
FALLBACK_TYPES = ['string',
                  'text',
                  'lines',]

class ContentTypesMultilingualPatcher(object):
    """ Utility para aplicar los parches de soporte multilenguaje
        a un ContentType en particular
    """
    implements(IContentTypesMultilingualPatcher)

    def patch(self, klass, replace_accessors=False):
        """ Incorpora los metodos con fallback multi-lenguaje

            >>> import string
            >>> from Products.Archetypes.atapi import *
            >>> from Products.ATContentTypes.content.base import ATCTContent
            >>> from icsemantic.core.content.multilingual import ContentTypesMultilingualPatcher
            >>> from icsemantic.core.interfaces import IMultilingualContentMarker, IMultilingualGettersMarker

            >>> class MyContent(ATCTContent):
            ...     portal_type = meta_type = 'MyContent'
            ...     schema = Schema((
            ...         StringField('some_field', storage=AnnotationStorage()),
            ...         StringField('_other_field'),
            ...         ))

            >>> registerType(MyContent, 'Archetypes')

            >>> hasattr(MyContent, 'getSome_field')
            True
            >>> hasattr(MyContent, 'getMultilingualSome_field')
            False

            >>> original_getter = getattr(MyContent, 'getSome_field')
            >>> ccpatcher = ContentTypesMultilingualPatcher()
            >>> ccpatcher.patch(MyContent)

            >>> IMultilingualContentMarker.implementedBy(MyContent)
            True
            >>> IMultilingualGettersMarker.implementedBy(MyContent)
            False
            >>> hasattr(MyContent, 'getSome_field')
            True
            >>> hasattr(MyContent, 'getMultilingualSome_field')
            True
            >>> original_getter == getattr(MyContent, 'getSome_field')
            True

            >>> ccpatcher.unpatch(MyContent)
            >>> IMultilingualContentMarker.implementedBy(MyContent)
            False
            >>> IMultilingualGettersMarker.implementedBy(MyContent)
            False
            >>> ccpatcher.patch(MyContent, replace_accessors=True)

            >>> IMultilingualContentMarker.implementedBy(MyContent)
            True
            >>> IMultilingualGettersMarker.implementedBy(MyContent)
            True
            >>> hasattr(MyContent, 'getSome_field')
            True
            >>> hasattr(MyContent, 'getMultilingualSome_field')
            True
            >>> original_getter == getattr(MyContent, 'getSome_field')
            False
            >>> getattr(MyContent, 'getSome_field') == getattr(MyContent, 'getMultilingualSome_field')
            True
            >>> original_getter == getattr(MyContent, '_old_getSome_field')
            True

        """
        if not IATContentType.isImplementedByInstancesOf(klass):
            # vamos a intentar conseguir el klass por el nombre
            portal = getSite()
            archetype_tool = getToolByName(portal, 'archetype_tool')
            for type in archetype_tool.listRegisteredTypes():
                if type['meta_type'] == klass:
                    klass = type['klass']
#        import pdb;pdb.set_trace()
##        assert IATContentType.isImplementedByInstancesOf(klass)

        if IMultilingualContentMarker.implementedBy(klass):
            return

        def getMultilingualField(self, field_name, fallback=True):
            """
            """
            field = self.getField(field_name)
            if field is None:
                raise KeyError("Cannot find field with name %s" % field_name)

            value = field.get(self)
            if not IMultilingualContentMarker.providedBy(self) or \
                field.isLanguageIndependent(self) or \
                not fallback or \
                field_name in NOT_FALLBACK_FIELDS:
                # si es independiente del lenguaje o pedimos que no haga
                # fallback lo devolvemos sea cual sea el valor
                # o las preferencias del usuario
                # tampoco hacemos fallback para el campo language
                return value

            translations = self.getTranslations()
            current_lang = self.getLanguage()
            if fallback and current_lang and len(translations) > 1:
                try:
                    icsemantic_lang_util = queryUtility(IUserPreferredLanguages,
                                                      name='icsemantic_preferred_languages')
                    request=getattr(self, 'REQUEST', None)
                    langs = icsemantic_lang_util.getPreferredLanguages(request=request)
                    langs += [current_lang]
                    for lang in langs:
                        if translations.has_key(lang):
                            inst = translations[lang][0]
                            field = inst.getField(field_name)
                            if field:
                                value = field.get(inst)
                            if not IFieldEmptiness(field)(inst):
                                break
                except:
                    pass
            return value

        if not hasattr(klass, 'getMultilingualField'):
            setattr(klass, 'getMultilingualField', getMultilingualField)

        fields = klass.schema.fields()
        for field in fields:
            name = field.getName()
#            if name is 'description': import pdb;pdb.set_trace()
            if field.type in FALLBACK_TYPES and \
               name not in NOT_FALLBACK_FIELDS and \
               not field.isLanguageIndependent(field):
                makeMethod(klass, field)
                def getMultilingualAccessor(self, field):
                    """Return the accessor method for getting data out of this
                    field"""
                    if field.multilingual_accessor:
                        accessor = getattr(self, field.multilingual_accessor, None)
                    if not accessor and field.accessor:
                        accessor = getattr(self, field.accessor, None)
                    return accessor
                setattr(klass, 'getMultilingualAccessor', getMultilingualAccessor)
                if replace_accessors:
                    # replace fields accessors
                    getName = field.accessor
                    getMultilingualName = "getMultilingual%s" % capitalize(name)
                    if hasattr(klass, getName) and \
                       hasattr(klass, getMultilingualName):
                        getMethod = getattr(klass, getName)
                        getMultilingualMethod = getattr(klass, getMultilingualName)
                        setattr(klass, '_old_%s' % getName, getMethod)
                        setattr(klass, getName, getMultilingualMethod)
                        classImplements(klass, IMultilingualGettersMarker)
                classImplements(klass, IMultilingualContentMarker)

    def unpatch(self, klass):
        """ Remueve los metodos con fallback multi-lenguaje

            >>> import string
            >>> from Products.Archetypes.atapi import *
            >>> from Products.ATContentTypes.content.base import ATCTContent
            >>> from icsemantic.core.content.multilingual import ContentTypesMultilingualPatcher

            >>> class MyContent(ATCTContent):
            ...     portal_type = meta_type = 'MyContent'
            ...     schema = Schema((
            ...         StringField('some_field', storage=AnnotationStorage()),
            ...         StringField('_other_field'),
            ...         ))

            >>> registerType(MyContent, 'Archetypes')

            >>> hasattr(MyContent, 'getSome_field')
            True
            >>> hasattr(MyContent, 'getMultilingualSome_field')
            False

            >>> ccpatcher = ContentTypesMultilingualPatcher()
            >>> ccpatcher.patch(MyContent)

            >>> hasattr(MyContent, 'getSome_field')
            True
            >>> hasattr(MyContent, 'getMultilingualSome_field')
            True

            >>> ccpatcher = ContentTypesMultilingualPatcher()
            >>> ccpatcher.unpatch(MyContent)

            >>> hasattr(MyContent, 'getSome_field')
            True
            >>> hasattr(MyContent, 'getMultilingualSome_field')
            False

        """
        if not IATContentType.isImplementedByInstancesOf(klass):
            # vamos a intentar conseguir el klass por el nombre
            portal = getSite()
            archetype_tool = getToolByName(portal, 'archetype_tool')
            for type in archetype_tool.listRegisteredTypes():
                if type['meta_type'] == klass:
                    klass = type['klass']
#        assert IATContentType.isImplementedByInstancesOf(klass)

        if IMultilingualContentMarker.implementedBy(klass):
            fields = klass.schema.fields()
            for field in fields:
                methodName = "getMultilingual%s" % capitalize(field.getName())
                if hasattr(klass, methodName):
                    try:
                        delattr(klass, methodName)
                    except:
                        pass
                if IMultilingualGettersMarker.implementedBy(klass):
                    name = field.getName()
                    getName = field.accessor
                    getOldName = "_old_%s" % getName
                    if hasattr(klass, getName) and hasattr(klass, getOldName):
                        getOldMethod = getattr(klass, getOldName)
                        setattr(klass, getName, getOldMethod)
                        try:
                            delattr(klass, getOldName)
                        except:
                            pass

            if hasattr(klass, 'getMultilingualField'):
                try:
                    delattr(klass, 'getMultilingualField')
                except:
                    pass

            classDoesNotImplement( klass, IMultilingualContentMarker)
            classDoesNotImplement( klass, IMultilingualGettersMarker)

def makeMethod(klass, field):
    name = field.getName()
    def generatedMultilingualAccessor(self, fallback = True):
        def who_called_me():
            try:
                1/0
            except ZeroDivisionError:
                return sys.exc_info()[2].tb_frame.f_back.f_back.f_code.co_name
        # TODO: tratar de encontrar un mejor metodo que este...
        who=who_called_me()
#        import pdb;pdb.set_trace()
        if who == '_get_object_datum':
            fallback = False

        value = self.getMultilingualField(name, fallback)
#        if value == 'ATDocument de prueba.':
#            import pdb;pdb.set_trace()
        return value
    method = generatedMultilingualAccessor
    methodName = "getMultilingual%s" % capitalize(name)
    method = function(method.func_code,
                      method.func_globals,
                      methodName,
                      method.func_defaults,
                      method.func_closure,
             )
    if not hasattr(klass, methodName):
        setattr(klass, methodName, method)
    field.multilingual_accessor = methodName
