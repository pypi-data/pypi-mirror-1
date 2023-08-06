###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: layer.py 347 2007-03-15 14:16:30Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.viewlet.interfaces import IViewletManager

import z3c.layer.ready2go


class IZMIBrowserLayer(z3c.layer.ready2go.IReady2GoBrowserLayer):
    """The ZMI browser layer."""


# ZAM viewlet manager
class ICSS(IViewletManager):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


class IBreadcrumb(IViewletManager):
    """Breadcrumb viewlet manager."""


class ISideBar(IViewletManager):
    """SideBar viewlet manager."""
