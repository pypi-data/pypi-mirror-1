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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.i18nmessageid
import zope.error.interfaces

from z3c.form import form
from z3c.form import field
from z3c.form import button
#so far we don't have z3c.form 2.0 use Text
#from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.formui import layout
from z3c.pagelet import browser

from p01.zmi import interfaces
_ = zope.i18nmessageid.MessageFactory('p01')


class EditErrorLog(layout.FormLayoutSupport, form.Form):

    zope.interface.implements(interfaces.IErrorReportingUtilityPage)

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    ignoreContext = True
    _content = None

    fields = field.Fields(interfaces.IErrorReportingUtilityManager)

    #so far we don't have z3c.form 2.0 use Text
    #fields['ignored_exceptions'].widgetFactory = TextLinesFieldWidget

    @property
    def content(self):
        if self._content is None:
            self._content = zope.component.getUtility(
            zope.error.interfaces.IErrorReportingUtility)
        return self._content

    def getContent(self):
        return self.content

    def updateProperties(self, keep_entries, copy_to_zlog=None,
                         ignored_exceptions=None):
        if copy_to_zlog is None:
            copy_to_zlog = 0
        if ignored_exceptions is None:
            ignored_exceptions = u''
        #so far we don't have z3c.form 2.0 use Text
        ignored_exceptions = tuple(
            unicode(v) for v in ignored_exceptions.splitlines())
        self.content.setProperties(keep_entries, copy_to_zlog,
            ignored_exceptions)

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        keep_entries = data['keep_entries']
        copy_to_zlog = data['copy_to_zlog']
        ignored_exceptions = data['ignored_exceptions']
        self.updateProperties(keep_entries, copy_to_zlog, ignored_exceptions)
        self.status = self.successMessage


class Errors(browser.BrowserPagelet):
    """Error listing page."""

    zope.interface.implements(interfaces.IErrorReportingUtilityPage)

    @property
    def values(self):
        util = zope.component.getUtility(
            zope.error.interfaces.IErrorReportingUtility)
        return util.getLogEntries()


class Error(browser.BrowserPagelet):
    """Show error page."""

    zope.interface.implements(interfaces.IErrorReportingUtilityPage)

    errorId = None

    @property
    def logEntry(self):
        """Return log entry if given in request."""
        if self.errorId is not None:
            util = zope.component.getUtility(
                zope.error.interfaces.IErrorReportingUtility)
            return util.getLogEntryById(self.errorId)

    def update(self):
        self.errorId = self.request.get('id')
        super(Error, self).update()


class ErrorAsText(Error):
    """Show error as text."""