# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setuphandlers.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
""" CMFDefault setup handlers.

"""
from StringIO import StringIO

from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from zope.component import getUtility
from zope.app.component.hooks import setSite
from zope.app.component.interfaces import ISite, IPossibleSite
from Products.CMFCore.utils import getToolByName
from Products.Five.site.localsite import enableLocalSiteHook

import interfaces
from config import HAS_PLONE3

def ensure_site(context):
  """Ensure the given context implements ISite.  The importance of
  this method is that it will ensure the given context is an ISite
  regardless of the Zope version (Zope 2.9 had a really hacked up
  SiteManager mechanism we have to account for).

      >>> from zope.app.component.interfaces import ISite, IPossibleSite
      >>> from OFS.Folder import Folder
      >>> if not IPossibleSite.implementedBy(Folder):
      ...    from zope import interface
      ...    from Products.Five.site.metaconfigure import (FiveSite,
      ...                                                  classSiteHook)
      ...    classSiteHook(Folder, FiveSite)
      ...    interface.classImplements(Folder, IPossibleSite)
      >>> om = Folder('foo')

      >>> ISite.providedBy(om)
      False

      >>> from iccommunity.core.setuphandlers import ensure_site
      >>> ensure_site(om)
      >>> ISite.providedBy(om)
      True

  """
  if not IPossibleSite.providedBy(context):
      if hasattr(context, 'getPhysicalPath'):
          p = '/'.join(context.getPhysicalPath())
      elif hasattr(context, 'getId'):
          p = context.getId()
      elif hasattr(context, 'id'):
          p = id
      else:
          p = str(context)

      raise TypeError('The object, "%s", is not an IPossibleSite' % p)

  if not ISite.providedBy(context):
    enableLocalSiteHook(context)
    setSite(context)

  if not ISite.providedBy(context):
    raise TypeError('Somehow trying to configure "%s" as an ISite '
                    'has failed' % '/'.join(context.getPhysicalPath()))

def setup_site(portal, out):
    """

        >>> from iccommunity.core import interfaces
        >>> from zope.app.component.hooks import setSite
        >>> setSite(portal)

        >>> sm = portal.getSiteManager()
        >>> pmct = sm.queryUtility(interfaces.IPlatecomManagementContentTypes,
        ...                        name='iccommunity.configuration')
        >>> pmct # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        <PlatecomManagementContentTypes at /plone.../>

        >>> pmct.fallback_types = []

        >>> pmas = sm.queryUtility(interfaces.IicCommunityManagementAdvancedSearchOptions,
        ...                        name='platecom.advancedsearch')
        >>> pmas.include_ontocatalog_criteria == False
        True

    """
    alsoProvides(portal, interfaces.IicCommunitySite)
    sm = portal.getSiteManager()

def importVarious(context):
  """ Import various settings.

  This provisional handler will be removed again as soon as full handlers
  are implemented for these steps.
  """
  site = context.getSite()
  out = StringIO()
  logger = context.getLogger("iccommunity.core")

  ensure_site(site)
  setup_site(site, out)

  print >> out, 'Various settings imported.'

  logger.info(out.getvalue())
  return out.getvalue()

def unimportVarious(context):
  """ Import various settings.

  This provisional handler will be removed again as soon as full handlers
  are implemented for these steps.
  """
  site = context.getSite()
  out = StringIO()
  logger = context.getLogger("iccommunity.core")

  print >> out, 'Various settings unimported.'

  logger.info(out.getvalue())
  return out.getvalue()
