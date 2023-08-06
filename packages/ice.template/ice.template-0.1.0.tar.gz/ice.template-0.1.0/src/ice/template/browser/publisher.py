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

from zope.location import LocationProxy
from zope.publisher.interfaces import browser, NotFound
from zope.component import queryMultiAdapter, getSiteManager
from zope.component.interfaces import ComponentLookupError, IDefaultViewName
from zope.interface import implements, providedBy

class TemplatesPublisher(object):
    implements(browser.IBrowserPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        for n, adapter in self.context.getAllTemplates():
            if n == name:
                return LocationProxy(
                    adapter, container=self.context, name=name)

        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view
        raise NotFound(self.context, name, request)

    def browserDefault(self, request):
        name = getSiteManager(self.context).adapters.lookup(
            map(providedBy, (object, request)), IDefaultViewName)
        if name is not None:
            return self.context, (name,)
        raise ComponentLookupError(
            "Couldn't find default view name", self.context, request)
