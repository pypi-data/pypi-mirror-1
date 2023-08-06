#-*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#   Copyright (c) 2007-2008 Gregor Giesen <giesen@zaehlwerk.net>            #
#                                                                           #
# This program is free software; you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation; either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################
"""
$Id$
"""
__docformat__ = 'reStructuredText'
from zw.schema.i18n import MessageFactory as _

import zope.schema
import zope.schema.interfaces
import zope.component
import zope.interface
from zope.app.intid.interfaces import IIntIds

from zw.schema.reference.interfaces import IReference


class Reference(zope.schema.Field):
    """A field to an persitent object referencable by IntId.
    """
    zope.interface.implements(IReference)
    
    def _validate(self, value):
        super(Reference, self)._validate(value)
        
        intids = zope.component.getUtility(IIntIds) # , context=value)
        intids.getId(value)
        
    def get(self, object):
        id = super(Reference, self).get(object)

        intids = zope.component.getUtility(IIntIds, context=object)
        return intids.queryObject(id)
        

    def set(self, object, value):
        intids = zope.component.getUtility(IIntIds, context=object)
        id = intids.getId(value)
        super(Reference, self).set(object, id)
