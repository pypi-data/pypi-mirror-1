# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: annotations.py 243 2008-06-11 19:45:26Z crocha $
#
# end: Platecom header
from zope.interface import implements
from zope.app.annotation.interfaces import IAttributeAnnotatable, IAnnotations
from persistent.dict import PersistentDict

class KeywordBasedAnnotations(object):
    implements(IAttributeAnnotatable)

    _anno_key = 'icSemanticANNO'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self._metadata = annotations.get(self._anno_key, None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations[self._anno_key] = self._metadata
