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

import re

import zope.schema
import zope.schema.interfaces
import zope.interface

from zw.schema.email.interfaces import IEmail, InvalidEmail

_isemail = re.compile( 
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}" ).match

class Email(zope.schema.Field):
    """A textline field containing an email address.
    """
    _type = str
    
    zope.interface.implements(IEmail, zope.schema.interfaces.IFromUnicode)
    
    def _validate(self, value):
        super(Email, self)._validate(value)

        if _isemail(value) is None:
            raise InvalidEmail(value)
        

    def fromUnicode(self, u):
        """
        """
        v = str(u)
        self.validate(v)
        return v

