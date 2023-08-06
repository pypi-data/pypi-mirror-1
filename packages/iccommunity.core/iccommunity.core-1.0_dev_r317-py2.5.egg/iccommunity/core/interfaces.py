# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: interfaces.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
""" iccommunity.core interfaces.
"""
# pylint: disable-msg=W0232,R0903

from zope import schema
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from iccommunity.core.i18n import _

class IicCommunitySite(Interface):
    """ represents a platecom installation, should be a local site
        with local components installed
    """

class IPlatecomConfiglet(Interface):
    """ platecom configlet
    """

