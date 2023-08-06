# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: base.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""
Clases de base para vistas y formularios

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

import sys
from datetime import datetime
import zope
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import locales, LoadLocaleError
from zope.formlib import form
from zope.formlib.namedtemplate import NamedTemplate, \
                                       NamedTemplateImplementation
try:
    from zope.lifecycleevent import ObjectModifiedEvent
except:
    from zope.app.event.objectevent import ObjectModifiedEvent

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate import ViewPageTemplateFile as ZopeViewPageTemplateFile
from Products.Five.formlib import formbase

from iccommunity.core.i18n import _

class BaseView( object ):
    """ So this mixin fixes some issues with doing zope3 in zope2
        for views specifically it puts a debug attribute on the request
        which some view machinery checks for secondly it lookups the
        user locale, and attaches it as an attribute on the request where
        the i10n widget machinery expects to find it.
    """

    def setupEnvironment( self, request ):
        """ Si request.debug no existe lo definimos como False """
        if not hasattr( request, 'debug'):
            request.debug = False

    def setupLocale( self, request ):
        """ Slightly adapted from zope.publisher.http.HTTPRequest.setupLocale
            Nos aseguramos que exista el request.locale
        """
        if getattr( request, 'locale', None) is not None:
            return

        envadapter = IUserPreferredLanguages(request, None)
        if envadapter is None:
            request.locale = locales.getLocale(None, None, None)
            return

        langs = envadapter.getPreferredLanguages()
        for httplang in langs:
            parts = (httplang.split('-') + [None, None])[:3]
            try:
                request.locale = locales.getLocale(*parts)
                return
            except LoadLocaleError:
                # Just try the next combination
                pass
        else:
            # No combination gave us an existing locale, so use the default,
            # which is guaranteed to exist
            request.locale = locales.getLocale(None, None, None)

class BaseFormView( formbase.EditFormBase, BaseView ):
    """ Definimos una clase de base para los forms, que tiene
        una apariencia mas compatible con plone.
    """

    template = ViewPageTemplateFile('templates/form.pt')

    action_url = "" # NEEDED
    hidden_form_vars = None # mapping of hidden variables to pass through on the form

    def hidden_inputs( self ):
        if not self.hidden_form_vars: return ''
        return make_hidden_input( **self.hidden_form_vars )

    hidden_inputs = property( hidden_inputs )

    def __init__( self, context, request ):
        # setup some compatiblity
        self.context = context
        self.request = request
        self.setupLocale( request )
        self.setupEnvironment( request )
        super( BaseFormView, self).__init__( context, request )

class BaseSettingsForm( BaseFormView, BaseView ):
    """ Definimos una clase de base para los forms de
        configuracion.
    """
    options = None
#    template = NamedTemplate("settings.form")
    template = ViewPageTemplateFile('templates/settings-page.pt')

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        try:
            if form.applyChanges(self.context,
                                 self.form_fields,
                                 data,
                                 self.adapters):
                zope.event.notify(
                    ObjectModifiedEvent(self.context)
                    )
                self.status = _(
                    "Updated on ${date_time}",
                    mapping={'date_time': str(datetime.utcnow())}
                    )
            else:
                self.status = _('No changes')
        except Exception, e:
            self.status = _(e)

settings_form_template = NamedTemplateImplementation(
                            ZopeViewPageTemplateFile('templates/settings-page.pt'),
                            BaseSettingsForm)
