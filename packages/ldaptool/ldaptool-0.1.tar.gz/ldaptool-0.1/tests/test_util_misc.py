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
from ldaptool.util.misc import *


class IsIterableTestCase(unittest.TestCase):

    def test_isiterable(self):

        self.assert_(is_iterable([]))
        self.assert_(is_iterable({}))
        self.assert_(is_iterable(iter([])))
        self.assert_(is_iterable(""))
        self.assert_(not is_iterable(1))
        self.assert_(not is_iterable(True))


class KeyMappedDictTestCase(unittest.TestCase):

    def test_create(self):
        d = KeyMappedDict()
        self.assertFalse(d.allow_unknown_keys)
        self.assertEquals(len(d), 0)
        self.assertEquals(d.key_map, {})
        self.assertEquals(repr(d),
            "KeyMappedDict({}, allow_unknown_keys=False, case_sensitive=True, "
            "key_map=[])"
        )
        d = KeyMappedDict(
            {'a': "foo", 'b': "bar"},
            allow_unknown_keys=True,
            key_map=None
        )
        self.assertTrue(d.allow_unknown_keys)
        self.assertEquals(len(d), 2)
        self.assertEquals(d.key_map, {})
        self.assertEquals(repr(d),
            "KeyMappedDict({'a': 'foo', 'b': 'bar'}, allow_unknown_keys=True, "
            "case_sensitive=True, key_map=[])"
        )
        self.assertRaises(KeyError, KeyMappedDict, {'a': "foo", 'b': "bar"})
        d = KeyMappedDict({'a': "foo", 'b': "bar"}, key_map=[('a',['b'])])
        self.assertFalse(d.allow_unknown_keys)
        self.assertEquals(len(d), 1)
        self.assertEquals(d['a'], "bar")
        self.assertEquals(d.key_map, {'a': 'a', 'b': 'a'})
        self.assertEquals(repr(d),
            "KeyMappedDict({'a': 'bar'}, allow_unknown_keys=False, "
            "case_sensitive=True, key_map=[('a', ['b'])])"
        )

    def test_key_map(self):
        d = KeyMappedDict()
        self.assertEquals(d.key_map, {})
        try:
            d['a'] = "foo"
            self.fail("Failed to raise KeyError.")
        except KeyError, e:
            self.assertEquals(str(e), "'Illegal key: a'")
        d.add_key('key1', ['key1_alias1', 'key1_alias2'])
        self.assertEquals(d.key_map, {
            'key1': 'key1',
            'key1_alias1': 'key1',
            'key1_alias2': 'key1'
        })
        d['key1'] = "value1"
        self.assertEquals(d.items(), [('key1', "value1")])
        self.assertEquals(d['key1'], "value1")
        self.assertEquals(d['key1_alias1'], "value1")
        self.assertEquals(d['key1_alias2'], "value1")
        d['key1_alias1'] = "value2"
        self.assertEquals(d.items(), [('key1', "value2")])
        self.assertEquals(d['key1'], "value2")
        self.assertEquals(d['key1_alias1'], "value2")
        self.assertEquals(d['key1_alias2'], "value2")
        try:
            d['key1_alias3'] = "value3"
            self.fail("Failed to raise KeyError")
        except KeyError:
            pass
        d.add_key('key2')
        self.assertEquals(d.key_map, {
            'key1': 'key1',
            'key1_alias1': 'key1',
            'key1_alias2': 'key1',
            'key2': 'key2'
        })
        d.remove_alias('key1_alias1')
        self.assertEquals(d.key_map, {
            'key1': 'key1',
            'key1_alias2': 'key1',
            'key2': 'key2'
        })
        self.assertRaises(KeyError, d.remove_alias, 'key1')
        self.assertRaises(KeyError, d.remove_key, 'key1_alias1')
        self.assertRaises(KeyError, d.remove_key, 'foo')
        d.remove_key('key1')
        self.assertEquals(d.key_map, {
            'key2': 'key2'
        })


    def test_case_sensitivity(self):
        d = KeyMappedDict(case_sensitive=False)
        d.add_key('Key1')
        self.assertEquals(d.key_map, {'key1': 'Key1'})
        d['key1'] = "value1"
        self.assertEquals(d.items(), [('Key1', "value1")])
        self.assertEquals(d['key1'], "value1")
        self.assertEquals(d['Key1'], "value1")
        self.assertEquals(d['KEY1'], "value1")
        d['KEY1'] = "value2"
        self.assertEquals(d.items(), [('Key1', "value2")])
        self.assertEquals(d['key1'], "value2")
        self.assertEquals(d['Key1'], "value2")
        self.assertEquals(d['KEY1'], "value2")
        del d['KeY1']
        self.assertEquals(d.items(), [])
        try:
            d['key2'] = "foo"
            self.fail("Failed to raise KeyError.")
        except KeyError:
            pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IsIterableTestCase))
    suite.addTest(unittest.makeSuite(KeyMappedDictTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')

