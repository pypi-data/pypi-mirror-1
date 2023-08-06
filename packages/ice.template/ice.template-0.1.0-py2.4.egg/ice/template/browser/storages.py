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
from zope.component import getAllUtilitiesRegisteredFor
from zope.dublincore.interfaces import IZopeDublinCore
from ice.template.interfaces import ITemplates
from ice.template import _

class Pagelet(table.Table):

    @property
    def values(self):
        return getAllUtilitiesRegisteredFor(ITemplates, self.context)

class TitleLinkColumn(column.IndexLinkColumn):

    header = _(u'Name')

    def getLinkContent(self, item):
        return IZopeDublinCore(item).title or super(
            TitleLinkColumn, self).getLinkContent(item)
