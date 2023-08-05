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
import unittest
import zope.testing.doctest
from zope.app.testing import placelesssetup

def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite('README.txt',
                                          setUp=placelesssetup.setUp,
                                          tearDown=placelesssetup.tearDown,
                                          optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                                          zope.testing.doctest.ELLIPSIS),
        ))
