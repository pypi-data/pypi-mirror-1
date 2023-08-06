##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: context.py 487 2007-06-17 00:42:12Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.contentprovider.interfaces import IContentProvider


class IAddMenu(IContentProvider):
    """Add menu item controlling tab."""


class IGlobalMenu(IContentProvider):
    """Global menu item controlling tab."""


class ISiteMenu(IContentProvider):
    """Server menu item controlling tab."""


class IContextMenu(IContentProvider):
    """Context menu item controlling tab."""
