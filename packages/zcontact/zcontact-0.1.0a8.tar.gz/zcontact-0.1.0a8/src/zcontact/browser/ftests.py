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
import os

from zope.app.testing.functional import ZCMLLayer, FunctionalDocFileSuite

import zcontact

dir = os.path.abspath(os.path.dirname(zcontact.__file__))
filename = os.path.join(dir, 'ftesting.zcml')

zcontact_functional_layer = ZCMLLayer(filename, __name__,
                                      'zcontact_function_layer')

def test_suite():
    suite = FunctionalDocFileSuite("BROWSER.txt")
    suite.layer = zcontact_functional_layer
    return unittest.TestSuite([suite])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
