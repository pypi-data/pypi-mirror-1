# Copyright (C) 2008  University of Bern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest
from ldaptool.settings import *


class SettingsTestCase(unittest.TestCase):

    def test_concat(self):
        """Test the Settings __add__, __radd__ and __iadd__ methods."""

        s = Settings({'a': 1, 'b': 2}) + Settings({'b': 3, 'c': 4})
        self.assertEquals(len(s), 3)
        self.assert_(isinstance(s, Settings))
        self.assertEqual(s['a'], 1)
        self.assertEqual(s['b'], 3)
        self.assertEqual(s['c'], 4)

        s = Settings({'a': 1, 'b': 2}) + {'b': 3, 'c': 4}
        self.assertEquals(len(s), 3)
        self.assert_(isinstance(s, Settings))
        self.assertEqual(s['a'], 1)
        self.assertEqual(s['b'], 3)
        self.assertEqual(s['c'], 4)

        s = {'a': 1, 'b': 2} + Settings({'b': 3, 'c': 4})
        self.assertEquals(len(s), 3)
        self.assert_(isinstance(s, Settings))
        self.assertEqual(s['a'], 1)
        self.assertEqual(s['b'], 3)
        self.assertEqual(s['c'], 4)

        s = Settings({'a': 1, 'b': 2})
        r = s
        s += {'b': 3, 'c': 4}
        self.assert_(s is r)
        self.assertEquals(len(s), 3)
        self.assert_(isinstance(s, Settings))
        self.assertEqual(s['a'], 1)
        self.assertEqual(s['b'], 3)
        self.assertEqual(s['c'], 4)

        s = Settings()
        s += {}
        self.assertEquals(len(s), 0)
        self.assert_(isinstance(s, Settings))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SettingsTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')

