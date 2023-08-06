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

import transaction

import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component.interfaces import IPossibleSite
from zope.site.interfaces import IRootFolder
from zope.site import folder
from zope.site import site
from z3c.pagelet import browser

from zope.app.appsetup.bootstrap import getInformationFromEvent
from zope.app.appsetup.interfaces import DatabaseOpenedWithRoot
from zope.app.publication.zopepublication import ZopePublication


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

    zope.interface.implements(IZMITestSite, IRootFolder)

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

    #def __init__(self, ctx,req):
    #    from pub.dbgpclient import brk; brk('192.168.32.1')
    #    print req.interaction.participations[0].principal.id


def bootstrapServer(event):
    """Subscriber to the IDataBaseOpenedEvent
    """
    db, connection, root, root_folder = getInformationFromEvent(event)

    if root_folder is None:
        # create
        obj = ZMITestSite(u'test')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

        # add as Application root
        root[ZopePublication.root_name] = obj

        # commit site to DB
        transaction.commit()

    connection.close()

    zope.event.notify(DatabaseOpenedWithRoot(db))
