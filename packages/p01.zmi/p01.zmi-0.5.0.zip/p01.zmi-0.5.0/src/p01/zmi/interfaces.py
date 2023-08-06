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

import zope.interface
import zope.schema
import zope.i18nmessageid

from z3c.form.interfaces import ITextAreaWidget

_ = zope.i18nmessageid.MessageFactory('p01')


class IErrorReportingUtilityManager(zope.interface.Interface):
    """Error reporting utility schema."""

    keep_entries = zope.schema.Int(
        title=_("Keep entries"),
        description=_("Count of entries in history"),
        default=20,
        required=True)

    copy_to_zlog = zope.schema.Bool(
        title=_("Copy to log"),
        description=_("Flag for copy errors to log"),
        default=False)


    #so far we don't have z3c.form 2.0 use Text
    #ignored_exceptions = zope.schema.Tuple(
    #    title=_("Ignore exceptions"),
    #    description=_("List of ignored exceptions"),
    #    value_type=zope.schema.TextLine(
    #        title=_("Ignored exception"),
    #        description=_("Name of the ignored exception."),
    #        default=u''),
    #    default=(),
    #    )

    ignored_exceptions = zope.schema.Text(
        title=_("Ignore exceptions"),
        description=_("List of ignored exceptions, separate with newlines"),
        default=u'',
        required=False,
        )


class IErrorReportingUtilityPage(zope.interface.Interface):
    """Error reporting utility page marker (used for menu item)."""


class IGeneratorSchema(zope.interface.Interface):
    """Schema for the minimal generator parameters"""

    seed = zope.schema.TextLine(
            title = _('Seed'),
            description =  _('A seed for the random generator'),
            default = u'sample',
            required=False,
            )
