##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.site.interfaces import IPossibleSite
from zope.site import folder
from zope.app.component import site
from z3c.pagelet import browser


###############################################################################
#
# ZMI test site
#
###############################################################################

class IZMITestSite(IPossibleSite, IAttributeAnnotatable):
    """ZMI test site interface."""

    __name__ = zope.schema.TextLine(
        title=u'Object name.',
        description=u'The object name.',
        default=u'ZMIDemoSite',
        missing_value=u'',
        required=True)

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the demo site.',
        default=u'',
        missing_value=u'',
        required=True)


class ZMITestSite(folder.Folder):
    """ZMI test site."""

    zope.interface.implements(IZMITestSite)

    title = FieldProperty(IZMITestSite['title'])

    def __init__(self, title):
        super(ZMITestSite, self).__init__()
        self.title = title

        # setup site manager
        self.setSiteManager(site.LocalSiteManager(self))

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class TestPage(browser.BrowserPagelet):
    """Test page."""
