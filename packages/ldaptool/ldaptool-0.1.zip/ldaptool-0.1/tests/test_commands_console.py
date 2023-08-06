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

from ldaptool.commands.console import *
from ldaptool.ldap import Server


class MockServer(Server):
    
    def __init__(self, uri=None):
        self.uri = uri
        self.instructions = []

    def search(self, *args, **kwargs):
        self.instructions.append(('search', args, kwargs)) 

    def add(self, *args, **kwargs):
        self.instructions.append(('add', args, kwargs)) 

    def delete(self, *args, **kwargs):
        self.instructions.append(('delete', args, kwargs)) 

    def modify(self, *args, **kwargs):
        self.instructions.append(('modify', args, kwargs)) 

    def rename(self, *args, **kwargs):
        self.instructions.append(('rename', args, kwargs)) 

    def passwd(self, *args, **kwargs):
        self.instructions.append(('passwd', args, kwargs)) 


class LdapCommandTestCase(unittest.TestCase):

    def test_fix_settings(self):
        pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LdapCommandTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')

