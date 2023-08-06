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


"""Tests for ldaptool."""


import os
import sys
import unittest


__all__ = ('suite', 'main')


def suite():
    suite = unittest.TestSuite()

    path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(path)

    for src in os.listdir(path):
        if not src.endswith('.py') or src == '__init__.py':
            continue
        module = __import__(os.path.basename(src[:-3]))
        suite.addTest(module.suite())

    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')


