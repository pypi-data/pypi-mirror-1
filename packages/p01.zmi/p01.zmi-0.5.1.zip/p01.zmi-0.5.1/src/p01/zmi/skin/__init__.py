##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: __init__.py 365 2007-03-25 03:36:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.contentprovider.interfaces
try:
    # old location
    from zope.component.interfaces import IDefaultViewName
except ImportError:
    # new location
    from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.browser import BrowserPage
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks
from zope.app.security.interfaces import IUnauthenticatedPrincipal

import p01.zmi.layer


class IZMIBrowserSkin(p01.zmi.layer.IZMIBrowserLayer):
    """The ``ZMI`` browser skin."""


class IHeaderProvider(zope.contentprovider.interfaces.IContentProvider):
    """Header provider."""


class SiteURL(BrowserPage):

    def __call__(self):
        return absoluteURL(hooks.getSite(), self.request)


class ManagementViewSelector(BrowserPage):
    """Redirect to the view with the default view name."""

    def __call__(self):
        url = '.'
        # not this is a very ugly pattern because the adapter is just a
        # name as string which doesn't provide the adaption pattern at all
        viewName = zope.component.getSiteManager(self.context).adapters.lookup(
            map(zope.interface.providedBy, (self.context, self.request)),
                IDefaultViewName)
        if viewName is not None:
            url = '%s/@@%s' % (absoluteURL(self.context, self.request),
                viewName)

        self.request.response.redirect(url)
        return u''


class SiteTitle(BrowserPage):

    def __call__(self):
        site = hooks.getSite()
        if site is not None and hasattr(site, 'title'):
            return site.title
        return u''


class ISAuthenticated(BrowserPage):

    def __call__(self):
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)
