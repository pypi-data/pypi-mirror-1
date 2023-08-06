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
""" Server Control View

$Id:$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.i18n
import zope.i18nmessageid
from ZODB.interfaces import IDatabase
from ZODB.FileStorage.FileStorage import FileStorageError
from zope.size import byteDisplay

import z3c.tabular.table
from z3c.table import column
from z3c.formui import form
from z3c.form import field
from z3c.form import button
from z3c.pagelet import browser
from z3c.template.template import getPageTemplate

_ = zope.i18nmessageid.MessageFactory('p01')


class DatabaseSelectorColumn(column.CheckBoxColumn):
    """Database selector column"""

    def getSortKey(self, item):
        return item['name']

    def getItemValue(self, item):
        return item['name']


class DatabaseNameColumn(column.Column):
    """Database Name column"""

    header = _(u'Database Name')

    def renderCell(self, item):
        return item['db'].getName()


class UtilityNameColumn(column.Column):
    """Database Name column"""

    header = _(u'Utility Name')

    def renderCell(self, item):
        return item['name']


class SizeColumn(column.Column):
    """Database Name column"""

    header = _(u'Size')

    def renderCell(self, item):
        db = item['db']
        size = db.getSize()  
        if not isinstance(size, (int, long, float)):
            return str(size)
        return zope.i18n.translate(byteDisplay(size))


class ZODBControl(z3c.tabular.table.FormTable):

    template = getPageTemplate()
    ignoreContext = True

    formErrorsMessage = _('There were some errors.')
    packNoItemsMessage = _('No database selected for pack')

    def setUpColumns(self):
        return [
            column.addColumn(self, DatabaseSelectorColumn, u'selector',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, UtilityNameColumn, u'utilName',
                             weight=2),
            column.addColumn(self, DatabaseNameColumn, u'databaseName',
                             weight=3),
            column.addColumn(self, SizeColumn, u'size',
                             weight=4),
            ]

    @property
    def values(self):
        return [{'db': db,
                 'name': str(name)}
                for name, db in zope.component.getUtilitiesFor(IDatabase)]

    @button.buttonAndHandler(_('Pack'), name='pack')
    def handlePack(self, action):
        if not len(self.selectedItems):
            self.status = self.packNoItemsMessage
            return
        # reset error list for catch new errors
        try:
            days = self.request.form.get('days') or '0'
            days = int(days.strip())
        except ValueError:
            self.status = _('Error: Invalid Number for days given')
            return
        status = []
        for info in self.selectedItems:
            dbName = info['name']
            db = info['db']
            db = zope.component.getUtility(IDatabase, name=dbName)
            try:
                db.pack(days=days)
                msg = _('Database registered as "${name}" successfully packed.',
                        mapping=dict(name=str(dbName)))
                status.append(zope.i18n.translate(msg))
            except FileStorageError, err:
                msg = _('ERROR packing database "${name}": ${err}',
                        mapping=dict(name=str(dbName), err=err))
                status.append(zope.i18n.translate(msg))
        if status:
            self.status = '<br />'.join(status)


    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handlePCancel(self, action):
        self.request.response.redirect(self.request.getURL())
        return u''
