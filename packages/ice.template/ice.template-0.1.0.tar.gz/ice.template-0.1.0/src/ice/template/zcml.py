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

import os.path
from zope.schema import TextLine
from zope.interface import Interface, classImplements
from zope.component.zcml import adapter
from zope.configuration.fields import Tokens, Path
from zope.configuration.exceptions import ConfigurationError
from interfaces import ITemplate, ITemplates

class ITemplateDirective(Interface):
    """Persistent Cheetah template directive."""

    name = TextLine(
        title=u"Unique name")

    title = TextLine(
        title=u"Title")

    storage = TextLine(
        title=u"Local name of the storage")

    variables = Tokens(
        title=u"Variables names",
        value_type=TextLine(),
        default=[],
        required=False)

    source = Path(
        title=u"Source template file, using Cheetah syntax.",
        default=None,
        required=False)

def read_src(path):
    f = open(path)
    src = f.read()
    f.close()
    return src

def templateDirective(_context, name, title, storage, variables=[], source=None):

    path = os.path.abspath(str(_context.path(source)))
    if not os.path.isfile(path):
        raise ConfigurationError("No such file", path)

    def __init__(self, context):
        self.context = context

    cdict = {'__init__':__init__, 'title':title, 'storage':storage,
             'variables':variables, 'source':read_src(path)}

    klass = type('Template', (), cdict)

    classImplements(klass, ITemplate)

    adapter(_context, (klass,), provides=ITemplate, for_=(ITemplates,), name=name)
