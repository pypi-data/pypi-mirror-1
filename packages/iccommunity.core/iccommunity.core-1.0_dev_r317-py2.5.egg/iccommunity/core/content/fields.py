# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: fields.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""
@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

import re

from zope.interface import implements

from iccommunity.core.interfaces import IFieldEmptiness

class TextFieldEmptiness(object):
    implements(IFieldEmptiness)

    def __init__(self, field):
        """
        Initialize our adapter
        """
        self.field = field

    def __call__(self, instance):
        value = self.field.get(instance)
        st=re.sub("<[^>]*>", "", value) # Elimino los tags
        st=re.sub("\W", "", st) # Elimino cosas que no correspondan a palabras.
        if (len(st) > 0):
           return False
        else:
           return True

class FieldEmptiness(object):
    implements(IFieldEmptiness)

    def __init__(self, field):
        """
        Initialize our adapter
        """
        self.field = field

    def __call__(self, instance):
        value = self.field.get(instance)
        if value:
           return False
        else:
           return True
