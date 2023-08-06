##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: __init__.py 451 2007-05-13 02:54:09Z roger.ineichen $
"""

from urllib import urlencode

import zope.interface
import zope.component
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks

from z3c.template.template import getPageTemplate

import p01.zmi.layer
from p01.zmi.skin import IHeaderProvider


class HeaderProvider(object):
    """Header content provider."""

    zope.interface.implements(IHeaderProvider)
    zope.component.adapts(zope.interface.Interface,
        p01.zmi.layer.IZMIBrowserLayer, zope.interface.Interface)

    template = getPageTemplate()

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    @property
    def loginURL(self):
        site = hooks.getSite()
        return '%s/loginForm.html?%s' % (
            absoluteURL(site, self.request), 
            urlencode({'camefrom': self.request.URL}))

    def update(self):
        pass

    def render(self):
        return self.template()
