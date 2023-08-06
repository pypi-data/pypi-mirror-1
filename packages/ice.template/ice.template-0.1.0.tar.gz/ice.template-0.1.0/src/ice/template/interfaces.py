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

from zope import interface, schema
from ice.template import _

class ITemplates(interface.Interface):
    """Manage persistent Cheetah templates"""

    def getTemplate(name):
        """Return template"""

    def setTemplate(name, text):
        """Store template"""

    def compileTemplate(name, data):
        """Return compiled template. 'data' is dictionary of the template
        variables and 'name' is template name."""

    def getVariables(name):
        """Return variables names"""

    def resetTemplate(name):
        """Reset template from source"""

    def getSource(name):
        """Get source text"""

    def getAllTemplates():
        """Return all templates registered for this storage"""

class ITemplate(interface.Interface):
    """Cheetah template"""

    title = schema.TextLine(
        title=u"Title")

    storage = schema.TextLine(
        title=u"Local name of the storage")

    variables = schema.List(
        title=u"Variables names",
        value_type=schema.TextLine())

    source = schema.TextLine(
        title=u"Source file path")
