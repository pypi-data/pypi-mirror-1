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

from zope.component import getUtility
from interfaces import ITemplates

class PersistentTemplate(object):
    
    def __init__(self, storage_name, template_name):
        self.__storage_name = storage_name
        self.__template_name = template_name

    def __get__(self, inst, klass):
         templates = getUtility(ITemplates, self.__storage_name)

         def compileTemplate(data={}):
             return templates.compileTemplate(self.__template_name, data)

         return compileTemplate
