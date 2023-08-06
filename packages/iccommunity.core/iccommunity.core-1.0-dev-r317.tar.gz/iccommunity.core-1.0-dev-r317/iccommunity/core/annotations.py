# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: annotations.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
from zope.interface import implements
try:
    from zope.annotation.interfaces import IAttributeAnnotatable, IAnnotations
except:
    from zope.app.annotation.interfaces import IAttributeAnnotatable, IAnnotations
from persistent.dict import PersistentDict

class KeywordBasedAnnotations(object):
    implements(IAttributeAnnotatable)

    _anno_key = 'icCommunityANNO'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self._metadata = annotations.get(self._anno_key, None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations[self._anno_key] = self._metadata
