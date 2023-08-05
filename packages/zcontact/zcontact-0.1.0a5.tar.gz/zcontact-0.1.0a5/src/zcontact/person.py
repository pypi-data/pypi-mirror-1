# ZContact - Web Based Contact Manager
# Copyright (C) 2007 Paul Carduner
#
# ZContact is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ZContact is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
from zope.interface import implements
from zope.app.container.btree import BTreeContainer 
from zope.app.container.contained import Contained
from zope.app.authentication import principalfolder
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.app import zapi
from zope.annotation.interfaces import IAttributeAnnotatable

from interfaces import IPerson, IPersonContainer, IPersonContained
import contact


class Person(principalfolder.InternalPrincipal, Contained):
    """An implementation of IPerson"""

    implements(IPerson, IPersonContained,
               IAttributeAnnotatable)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.login)

class PersonContainer(principalfolder.PrincipalFolder):
    """Container of persons"""

    implements(IPersonContainer,
               IAttributeAnnotatable)


def getPersonFromPrincipal(principal):
    """Adapter from IPrincipal to IPerson"""
    return contact.getZContactApplication()['users'][principal.id]
