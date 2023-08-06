##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: virtualsite.py 334 2007-03-15 01:38:06Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL
from zope.app.component import hooks

from z3c.menu.ready2go import item


# server control
class ErrorsMenuItem(item.ContextMenuItem):
    """Errors menu."""

    viewName = 'errors.html'
    weight = 1


class ErrorEditMenuItem(item.ContextMenuItem):
    """Error edit menu."""

    viewName = 'editError.html'
    weight = 2


class RuntimeMenuItem(item.ContextMenuItem):
    """Runtime menu item."""

    viewName = 'runtime.html'
    weight = 3


class ZODBControlMenuItem(item.ContextMenuItem):
    """ZODB control menu item."""

    viewName = 'ZODBControl.html'
    weight = 4


class GenerationsMenuItem(item.ContextMenuItem):
    """Generation management menu item."""

    viewName = 'generations.html'
    weight = 5


class SampleDataMenuItem(item.ContextMenuItem):
    """Sample data management menu item."""

    viewName = 'sampledata.html'
    weight = 6
