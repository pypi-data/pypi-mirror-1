##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Implementations of the basic policy components.

"""
__docformat__ = "reStructuredText"


import zope.app.intid.interfaces
import zope.component
import zope.dublincore.interfaces

import zc.sourcefactory.browser.source
import zc.sourcefactory.interfaces


# Term policies

class BasicTermPolicy(object):
    """A basic term policy.

    createTerm creates a FactoredTerm object.

    getTitle uses IDCDescriptiveProperties.title and falls back to
    `str`-representation of the value.
    """

    zope.interface.implements(zc.sourcefactory.interfaces.ITermPolicy)

    def createTerm(self, source, value, title, token, request):
        return zc.sourcefactory.browser.source.FactoredTerm(
            value, title, token)

    def getTitle(self, value):
        try:
            md = zope.dublincore.interfaces.IDCDescriptiveProperties(value)
        except TypeError:
            md = None

        if md:
            title = md.title
        else:
            title = str(value)
        return title


# Token policies

class BasicTokenPolicy(object):
    """A basic token policy.

    getToken adapts the value to IToken

    getValue iterates over the source comparing the tokens of the values to the
    token.
    """

    zope.interface.implements(zc.sourcefactory.interfaces.ITokenPolicy)

    def getValue(self, source, token):
        for value in source:
            if source.factory.getToken(value) == token:
                return value
        raise KeyError, "No value with token '%s'" % token

    def getToken(self, value):
        return zc.sourcefactory.interfaces.IToken(value)


class IntIdTokenPolicy(object):
    """A token policy based on intids."""

    zope.interface.implements(zc.sourcefactory.interfaces.ITokenPolicy)

    def getValue(self, source, token):
        iid = int(token)
        value = self.intids.getObject(iid)
        if value in self.source:
            return value
        else:
            raise LookupError("no value matching token: %r" % token)

    def getToken(self, value):
        return str(self.intids.getId(value))

    # We can't use zope.cachedescriptors.property.Lazy for this since
    # the source factory exists across the entire process, and is used
    # across different requests.  Using Lazy for this would result in
    # the wrong ZODB connection being used in most threads.
    #
    @property
    def intids(self):
        return zope.component.getUtility(
            zope.app.intid.interfaces.IIntIds)


# Value policies

class BasicValuePolicy(object):
    """An abstract basic value policy.

    `getValues()` is not implemented.

    The filter allows all values.
    """

    zope.interface.implements(zc.sourcefactory.interfaces.IValuePolicy)

    def filterValue(self, value):
        return True

class BasicContextualValuePolicy(BasicValuePolicy):
    """An abstract basic value policy.

    `getValues()` is not implemented.

    The filter allows all values.
    """

    zope.interface.implements(
        zc.sourcefactory.interfaces.IContextualValuePolicy)

    def filterValue(self, context, value):
        return True


# Standard combined policies

class BasicSourcePolicy(BasicValuePolicy, BasicTokenPolicy, BasicTermPolicy):
    pass


class BasicContextualSourcePolicy(
    BasicContextualValuePolicy, BasicTokenPolicy, BasicTermPolicy):
    pass


class IntIdSourcePolicy(BasicValuePolicy, IntIdTokenPolicy, BasicTermPolicy):
    pass
