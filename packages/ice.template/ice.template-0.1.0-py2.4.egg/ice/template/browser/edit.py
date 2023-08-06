### -*- coding: utf-8 -*- ####################################################
#
#  Copyright (C) 2009 Ilshad Habibullin <astoon.net at gmail.com>
#
#  This library is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#  for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Project homepage: <http://launchpad.net/ice.template>
#
##############################################################################

from Cheetah.Template import Template
from z3c.formui import form
from z3c.form import field, button
from zope.schema import Text
from ice.template import _

TFIELD_NAME = 'body'

class Pagelet(form.EditForm):
    form.extends(form.EditForm)
    
    fields = field.Fields(
        field.Field(Text(required=False), name=TFIELD_NAME))

    ignoreContext = True

    templates = property(lambda self: self.context.__parent__)
    tname = property(lambda self: self.context.__name__)
    preview = None

    def updateWidgets(self):
        super(Pagelet, self).updateWidgets()
        widget = self.widgets[TFIELD_NAME]
        if not self.request.get(widget.name):
            widget.value = self.templates.getTemplate(self.tname)

    def checkVariables(self):
        varnames = self.templates.getVariables(self.tname)
        variables = dict((v, u'***') for v in varnames)
        text = self.extractData()[0].get(TFIELD_NAME)
        try:
            return unicode(Template(text, variables))
        except:
            return None

    def applyChanges(self, data):
        if self.checkVariables() is not None:
            return super(Pagelet, self).applyChanges(data)
        self.noChangesMessage = _(u'There are some errors in the template')
        return None

    @button.buttonAndHandler(_(u'Reset from source'))
    def handleReset(self, action):
        self.widgets[TFIELD_NAME].value = self.templates.getSource(self.tname)

    @button.buttonAndHandler(_(u'Refresh'))
    def handleRefresh(self, action):
        self.widgets[TFIELD_NAME].value = self.templates.getTemplate(self.tname)

    @button.buttonAndHandler(_(u'Preview and Test'))
    def handlePreview(self, action):
        self.preview = self.checkVariables()
        self.status = self.preview is not None and _(u'Ok') or _(
            u'There are some errors in the template')

class TemplateTextField(object):

    query = lambda self, *args: self.get()
    canAccess = lambda self: True
    canWrite = lambda self: True

    def __init__(self, context, field):
        self.templates = context.__parent__
        self.name = context.__name__
        self.field = field

    def get(self):
        return self.templates.getTemplate(self.name)

    def set(self, value):
        self.templates.setTemplate(self.name, value)
