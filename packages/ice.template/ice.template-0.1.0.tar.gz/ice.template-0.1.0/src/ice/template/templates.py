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
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.component import getAdapter, getAdapters, getUtilitiesFor
from zope.interface import implements
from zope.location import ILocation
from interfaces import ITemplates, ITemplate

def getUtilityName(context):
    for name, utility in getUtilitiesFor(ITemplates, context):
        if utility == context:
            return name

class Templates(Persistent):
    implements(ITemplates, ILocation)

    __parent__ = __name__ = None

    def __init__(self):
        self._templates = OOBTree()
        super(Templates, self).__init__()

    def getTemplate(self, name):
        return self._templates.get(name) or self.resetTemplate(name)

    def setTemplate(self, name, text):
        self._templates[name] = text

    def compileTemplate(self, name, data={}):
        return str(Template(self.getTemplate(name), searchList=[data]))

    def getVariables(self, name):
        return getAdapter(self, ITemplate, name=name).variables

    def resetTemplate(self, name):
        result = self._templates[name] = self.getSource(name)
        return result

    def getSource(self, name):
        tmpl = getAdapter(self, ITemplate, name=name)
        if tmpl.storage == getUtilityName(self):
            return tmpl.source
        raise KeyError

    def getAllTemplates(self):
        uname = getUtilityName(self)
        for name, adapter in getAdapters([self], ITemplate):
            if adapter.storage == uname:
                yield name, adapter
