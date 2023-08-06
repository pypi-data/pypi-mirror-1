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
import zope.component
import zope.schema
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL
from zope.exceptions.interfaces import DuplicationError

from z3c.template.template import getPageTemplate
from z3c.pagelet import browser
from z3c.form.interfaces import IWidgets
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.formui import layout

from p01.sampler.interfaces import ISampleManager

_ = zope.i18nmessageid.MessageFactory('p01')


class Sampler(browser.BrowserPagelet):
    """Sample data managers."""

    def managers(self):
        return [name for name, util in 
                zope.component.getUtilitiesFor(ISampleManager)]

    def update(self):
        if 'manager' in self.request:
            managerName = self.request['manager']
            self.request.response.redirect(
                absoluteURL(self.context, self.request)+
                '/@@samplergenerator.html?manager="%s"'%(managerName))


class IGeneratorSchema(zope.interface.Interface):
    """Schema for the minimal generator parameters"""

    seed = zope.schema.TextLine(
            title = _('Seed'),
            description =  _('A seed for the random generator'),
            default = u'sample',
            required=False,
            )


class SamplerGenerator(form.Form):
    """Edit all generator parameters for a given manager"""

    subforms = []
    workDone = False
    errors = None

    @property
    def showGenerateButton(self):
        if self.request.get('manager', None) is None:
            return False
        return True

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()

    def update(self):
        managerName = self.request.get('manager', None)
        if managerName is not None:
            self.subforms = []
            manager = zope.component.getUtility(ISampleManager,
                name=managerName)
            plugins = manager.orderedPlugins()
            self.fields = field.Fields()
            subform = SingleGenerator(context=self.context,
                                      request=self.request,
                                      schema=IGeneratorSchema,
                                      prefix='generator')
            subform.fields = field.Fields(IGeneratorSchema)
            self.subforms.append(subform)
            for plugin in plugins:
                if plugin.generator.schema is None:
                    continue
                subform = SingleGenerator(context=self.context,
                                          request=self.request,
                                          plugin=plugin.generator,
                                          prefix=str(plugin.name))
                subform.fields = field.Fields(plugin.generator.schema)
                self.subforms.append(subform)
        super(SamplerGenerator, self).update()

    @button.buttonAndHandler(u'Validate',
        condition=lambda form: form.showGenerateButton)
    def handleValidate(self, action):
        managerName = self.request['manager']
        manager = zope.component.getUtility(ISampleManager, name=managerName)
        generatorData = {}
        for subform in self.subforms:
            subform.update()
            formData = {}
            data, errors = subform.widgets.extract()
            generatorData[subform.prefix] = data
        gen = generatorData.get('generator', {})
        seed = gen.get('seed', None)
        # first validate our sample data generator plugins
        errors = manager.validate(context=self.context, param=generatorData,
            seed=seed)
        if errors is not True:
            self.errors = errors
            self.status = _('Validation FAILED see errors for more information')
        else:
            self.status = _('Sucessfully validated')

    @button.buttonAndHandler(u'Generate',
        condition=lambda form: form.showGenerateButton)
    def handleGenerate(self, action):
        managerName = self.request['manager']
        manager = zope.component.getUtility(ISampleManager, name=managerName)
        generatorData = {}
        for subform in self.subforms:
            subform.update()
            formData = {}
            data, errors = subform.widgets.extract()
            generatorData[subform.prefix] = data
        gen = generatorData.get('generator', {})
        seed = gen.get('seed', None)
        # first validate our sample data generator plugins
        status = manager.validate(context=self.context, param=generatorData,
            seed=seed)
        if status is not True:
            self.status = "".join(status)
        else:
            try:
                self.workedOn = manager.generate(context=self.context, 
                    param=generatorData, seed=seed)
                self.workDone = True
            except DuplicationError:
                self.status = _('Duplidated item')

    @button.buttonAndHandler(u'Cleanup',
        condition=lambda form: form.showGenerateButton)
    def handleCleanup(self, action):
        managerName = self.request['manager']
        manager = zope.component.getUtility(ISampleManager, name=managerName)
        generatorData = {}
        for subform in self.subforms:
            subform.update()
            formData = {}
            data, errors = subform.widgets.extract()
            generatorData[subform.prefix] = data
        gen = generatorData.get('generator', {})
        seed = gen.get('seed', None)
        # first validate our sample data generator plugins
        status = manager.validate(context=self.context, param=generatorData,
            seed=seed)
        if status is not True:
            self.status = "".join(status)
        else:
            try:
                self.workedOn = manager.cleanup(context=self.context, 
                    param=generatorData, seed=seed)
                self.workDone = True
            except DuplicationError:
                self.status = _('Duplidated item')

    def manager(self):
        return self.request.get('manager', None)


class SingleGenerator(form.Form):
    """An editor for a single generator"""

    template = getPageTemplate('subform')

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()

    def __init__(self, context, request, plugin=None, schema=None, prefix=''):
        self.plugin = plugin
        self.schema = schema
        self.prefix = str(prefix) # must be a string in z3c.form
        super(SingleGenerator, self).__init__(context, request)

    def render(self):
        return self.template()

    def __call__(self):
        self.update()
        return self.render()