# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: admin.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""
admin setting and preferences
Solo vistas y forms

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

import os
from datetime import datetime

import zope
from zope import component
from zope.component import getUtility
from zope.formlib import form
from zope.app.form.browser import MultiSelectSetWidget
from zope.app.form.browser.itemswidgets import MultiSelectWidget \
        as BaseMultiSelectWidget, DropdownWidget, SelectWidget
from zope.app.form.browser import FileWidget

try:
    from zope.lifecycleevent import ObjectModifiedEvent
except:
    from zope.app.event.objectevent import ObjectModifiedEvent

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser import BrowserView
from Products.Five.formlib import formbase

from iccommunity.core import interfaces
from iccommunity.core import pkg_home
from iccommunity.core.i18n import _
from base import BaseSettingsForm
from widgets import OrderedMultiSelectionWidgetFactory, \
                    MultiSelectionWidgetFactory

class Overview( BrowserView ):
    """ Platecom config overview
    """

    def getVersion( self ):
        fh = open( os.path.join( pkg_home, 'version.txt') )
        version_string = fh.read()
        fh.close()
        return version_string

class UserOverview( BrowserView ):
    """ Platecom user config overview
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        super(UserOverview, self).__init__(context, request)

    def __call__(self):
        self.authenticated_member = self.context.portal_membership.getAuthenticatedMember()
        return super(UserOverview, self).__call__()

