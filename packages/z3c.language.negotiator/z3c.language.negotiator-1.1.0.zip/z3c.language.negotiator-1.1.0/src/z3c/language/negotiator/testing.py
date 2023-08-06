##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id: testing.py 106095 2009-11-29 04:51:14Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import INegotiator

import z3c.testing
from z3c.language.session.interfaces import ILanguageSession


###############################################################################
#
# Test component
#
###############################################################################

class LanguageSessionStub(object):
    
    zope.interface.implements(ILanguageSession)
    zope.component.adapts(IUserPreferredLanguages)

    def __init__(self, request):
        pass

    def getLanguage(self):
        return 'fr'


class EnvStub(object):
    zope.interface.implements(IUserPreferredLanguages)

    def __init__(self, langs=()):
        self.langs = langs

    def getPreferredLanguages(self):
        return self.langs


###############################################################################
#
# Public base tests
#
###############################################################################

class BaseTestINegotiator(z3c.testing.InterfaceBaseTest):
    """Resuable INegotiator base test."""

    def getTestInterface(self):
        return INegotiator
