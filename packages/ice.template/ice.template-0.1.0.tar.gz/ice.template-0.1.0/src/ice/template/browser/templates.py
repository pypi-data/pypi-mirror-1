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

from z3c.table import table, column
from zope.traversing.browser.absoluteurl import absoluteURL
from ice.template import _

class Pagelet(table.Table):
    
    @property
    def values(self):
        return self.context.getAllTemplates()

class BrowserViewLinkColumn(column.Column):

    header = _(u'Name')

    def renderCell(self, item):
        return u'<a href="%s">%s</a>' % (
            absoluteURL(self.context, self.request) + u'/' + item[0],
            getattr(item[1], 'title', None) or item[0])
