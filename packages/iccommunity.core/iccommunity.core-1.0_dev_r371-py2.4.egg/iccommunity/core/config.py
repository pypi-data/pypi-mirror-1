# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

import iccommunity.core
PACKAGE = iccommunity.core

PROJECTNAME = "iccommunity.core"
PACKAGENAME = "iccommunity.core"

DEPENDENCIES = []

from Products.CMFCore.permissions import SetOwnProperties
CONFIGLETS = ()
"""
    { 'id'         : 'iccommunity_member'
    , 'name'       : 'iccommunity'
    , 'action'     : 'string:${portal_url}/@@user-community-overview'
    , 'condition'  : ''
    , 'category'   : 'Member'
    , 'visible'    : 1
    , 'appId'      : PROJECTNAME
    , 'permission' : SetOwnProperties
    , 'imageUrl'   : '++resource++iccommunity.core.images/lgo16-iccommunity.png'
    },
    )
"""


GLOBALS = globals()
