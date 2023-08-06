##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

import zope.interface
import zope.component
import zope.location.interfaces
import zope.traversing.api
import zope.proxy
import z3c.breadcrumb.browser
import z3c.breadcrumb.interfaces

import p01.zmi.layer


class BreadcrumbProvider(z3c.breadcrumb.browser.Breadcrumbs):
    """Breadcrumbs implementation using IBreadcrum adapters."""

    zope.component.adapts(zope.location.interfaces.ILocation,
        p01.zmi.layer.IZMIBrowserLayer, zope.interface.Interface)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = context
        self.view = view

    def update(self):
        pass

    @property
    def crumbs(self):
        request = self.request

        objects = []
        try:
            parents = list(zope.traversing.api.getParents(self.context))
        except TypeError,e:
            parents = []
        for obj in ( [self.context] + parents):
            objects.append(obj)
            if zope.proxy.sameProxiedObjects(obj,
                request.getVirtualHostRoot()) or isinstance(obj, Exception):
                break

        objects.reverse()
        for object in objects:
            info = zope.component.queryMultiAdapter((object, self.request),
                z3c.breadcrumb.interfaces.IBreadcrumb)
            if info is not None:
                yield {'name': info.name,
                       'url': info.url,
                       'activeURL': info.activeURL}

    def render(self):
        bStr = u''
        crumbs = list(self.crumbs)
        if crumbs:
            for crumb in crumbs:
                if crumb['activeURL']:
                    bStr += ' &gt;&gt; <a href="%s" class="selected">%s</a>' %(
                        crumb['url'], crumb['name'])
                else:
                    bStr += ' &gt;&gt; <a href="%s">%s</a>' % (crumb['url'],
                        crumb['name'])
        return bStr
