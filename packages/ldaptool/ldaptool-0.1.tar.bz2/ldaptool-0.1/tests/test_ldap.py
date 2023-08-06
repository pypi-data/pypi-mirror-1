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
from inspect import getargspec

from ldaptool.ldap import *


class SafeStringTestCase(unittest.TestCase):

    def test_safe_chars(self):
        for i in xrange(0,256):
            self.assertEquals(chr(i) in SAFE_CHARS,
                # any value <= 127 decimal except NUL, LF, and CR
                0x01 <= i <= 0x09 or 0x0b <= i <= 0x0c or 0x0e <= i <= 0x7f
            )

    def test_safe_init_chars(self):
        for i in xrange(0, 256):
            self.assertEquals(chr(i) in SAFE_INIT_CHARS,
                # any value <= 127 except NUL, LF, CR, SPACE, colon (":", ASCII
                # 58 decimal) and less-than ("<" , ASCII 60 decimal)
                0x01 <= i <= 0x09 or 0x0b <= i <= 0x0c or 0x0e <= i <= 0x1f or \
                0x21 <= i <= 0x39 or 0x3b == i or 0x3d <= i <= 0x7f
            )

    def test_is_safe_string(self):
        self.assert_(is_safe_string(""))
        self.assert_(is_safe_string(u""))
        self.assert_(is_safe_string("A"))
        self.assert_(is_safe_string(u"A"))
        self.assert_(not is_safe_string("\x00"))
        self.assert_(not is_safe_string(u"\x00"))
        self.assert_(not is_safe_string("\x0a"))
        self.assert_(not is_safe_string(u"\x0a"))
        self.assert_(is_safe_string("Hello"))
        self.assert_(is_safe_string(u"Hello"))
        self.assert_(not is_safe_string(" Hello"))
        self.assert_(not is_safe_string(u" Hello"))
        self.assert_(not is_safe_string("Hell\x94"))
        self.assert_(not is_safe_string(u"Hell\x94"))
        self.assert_(not is_safe_string(u'\u5c0f\u7b20\u539f'))

    def test_get_safe_string(self):
        self.assertEquals(get_safe_string(""), "")
        self.assertEquals(get_safe_string(u""), "")
        self.assertEquals(get_safe_string("A"), "A")
        self.assertEquals(get_safe_string(u"A"), "A")
        self.assertEquals(get_safe_string("\x00"), "AA==")
        self.assertEquals(get_safe_string(u"\x00"), "AA==")
        self.assertEquals(get_safe_string("\x0a"), "Cg==")
        self.assertEquals(get_safe_string(u"\x0a"), "Cg==")
        self.assertEquals(get_safe_string("Hello"), "Hello")
        self.assertEquals(get_safe_string(u"Hello"), "Hello")
        self.assertEquals(get_safe_string(" Hello"), "IEhlbGxv")
        self.assertEquals(get_safe_string(u" Hello"), "IEhlbGxv")
        self.assertEquals(get_safe_string("Hell\x94"), "SGVsbJQ=")
        self.assertEquals(get_safe_string(u"Hell\x94"), "SGVsbMKU")
        self.assertEquals(get_safe_string(u'\u5c0f\u7b20\u539f'),"5bCP56yg5Y6f")


class MockServer(Server):
    """Mock server to test :meth:`Record.apply_to_server`."""

    def __init__(self, url=None):
        self.url = url
        self.calls = []

    def search(self, base, scope=Server.SCOPE_SUBTREE,
            filter='(objectClass=*)', attr_list=None, desc_only=False,
            timeout=-1, size_limit=0):
        self.calls.append(('search', {
            'base': base, 'scope': scope, 'filter': filter,
            'attr_list': attr_list, 'desc_only': desc_only, 'timeout': timeout,
            'size_limit': size_limit
        }))

    def add(self, dn, modlist):
        self.calls.append(('add', {'dn': dn, 'modlist': modlist}))

    def delete(self, dn):
        self.calls.append(('delete', {'dn': dn}))

    def modify(self, dn, modlist):
        self.calls.append(('modify', {'dn': dn, 'modlist': modlist}))

    def rename(self, dn, newrdn, newsuperior=None, delete=True):
        self.calls.append(('rename', {
            'dn': dn, 'newrdn': newrdn, 'newsuperior': newsuperior,
            'delete': delete
        }))

    def passwd(self, dn, oldpw=None, newpw=None):
        self.calls.append(('passwd', {
            'dn': dn, 'oldpw': oldpw, 'newpw': newpw
        }))


class ServerTestCase(unittest.TestCase):

    def assertArguments(self, cls, method, expected):
        computed = getargspec(getattr(cls, method))
        self.assertEquals(computed, expected,
            "Incorrect arguments for %s.%s. Expected:\n"
            "  %r\n"
            "but was:\n"
            "  %r" % (cls.__name__, method, computed, expected)
        )

    def test_constants(self):
        self.assertEquals(Server.MOD_ADD, 0x00)
        self.assertEquals(Server.MOD_DELETE, 0x01)
        self.assertEquals(Server.MOD_REPLACE, 0x02)
        self.assertEquals(Server.SCOPE_BASE, 0x00)
        self.assertEquals(Server.SCOPE_ONELEVEL, 0x01)
        self.assertEquals(Server.SCOPE_SUBTREE, 0x02)

    def test_arguments(self):
        classes = [Server, SynchronousServer, AsynchronousServer, MockServer]
        for cls in classes:
            self.assertArguments(cls, 'search', (['self', 'base', 'scope',
                'filter', 'attr_list', 'desc_only', 'timeout', 'size_limit'],
                None, None, (Server.SCOPE_SUBTREE, '(objectClass=*)', None,
                False, -1, 0))
            )
            self.assertArguments(cls, 'add', (['self', 'dn', 'modlist'],
                None, None, None)
            )
            self.assertArguments(cls, 'delete', (['self', 'dn'], None,
                None, None)
            )
            self.assertArguments(cls, 'modify', (['self', 'dn',
                'modlist'], None, None, None)
            )
            self.assertArguments(cls, 'rename', (['self', 'dn', 'newrdn',
                'newsuperior', 'delete'], None, None, (None, True))
            )
            self.assertArguments(cls, 'passwd', (['self', 'dn', 'oldpw',
                'newpw'], None, None, (None, None))
            )


class AttrValContainerTestCase(unittest.TestCase):

    def test_str(self):
        # TODO
        pass


class EntryTestCase(unittest.TestCase):


    def test_create_simple(self):
        entry = Entry("dc=example,dc=org")
        self.assertEquals(entry.dn, "dc=example,dc=org")

    def test_attributes(self):
        entry = Entry("dc=example,dc=org")

        self.assert_(entry['dn'], "dc=example,dc=org")
        entry['foo'] = 'bar1'
        self.assertEquals(entry['foo'], ['bar1'])
        entry['foo'] = 'bar2'
        self.assertEquals(entry['foo'], ['bar2'])
        entry['foo'] = ['bar3', 'bar4']
        self.assertEquals(entry['foo'], ['bar3', 'bar4'])
        self.assertRaises(KeyError, lambda: entry['bar'])
        from urllib2 import urlopen
        from os.path import abspath
        url = urlopen("file://%s" % abspath(__file__))
        entry['file'] = url
        self.assertEquals(entry['file'], [url])
        
        try:
            del entry['foo']
        except KeyError:
            fail("failed to delete existing attribute")
        try:
            del entry['bar']
            fail("KeyError not raised")
        except KeyError:
            pass
        try:
            del entry['dn']
            fail("KeyError not raised")
        except KeyError:
            pass

    def test_create_complex(self):
        from urllib2 import urlopen
        from os.path import abspath
        url = urlopen("file://%s" % abspath(__file__))
        entry = Entry("dc=example,dc=org", {
            'dc': 'example', 'objectClass': ['dcObject', 'top'],
            'cn': u"\u5c0f\u7b20\u539f",'file': url
        })
        self.assertEquals(entry.dn, "dc=example,dc=org")
        self.assertEquals(entry['dc'], ["example"])
        self.assertEquals(entry['objectClass'], ["dcObject", "top"])
        self.assertEquals(entry['cn'], [u"\u5c0f\u7b20\u539f"])
        self.assertEquals(entry['file'], [url])

    def test_iterators(self):
        entry = Entry("dc=example,dc=org")
        self.assertEquals(list(entry.iterkeys()), ['dn'])
        self.assertEquals(list(entry.itervalues()), ["dc=example,dc=org"])
        self.assertEquals(list(entry.iteritems()), [
            ('dn', "dc=example,dc=org")
        ])
        self.assertEquals(len(entry), 1)
        entry['foo'] = ['bar1','bar2']
        self.assertEquals(list(entry.iterkeys()), ['dn', 'foo'])
        self.assertEquals(list(entry.itervalues()), [
            "dc=example,dc=org", "bar1", "bar2"
        ])
        self.assertEquals(list(entry.iteritems()), [
            ('dn', "dc=example,dc=org", ), ('foo', "bar1"), ('foo', "bar2")
        ])
        self.assertEquals(len(entry), 3)
        entry['zoo'] = ['bear']
        self.assertEquals(list(entry.iterkeys()), ['dn', 'foo', 'zoo'])
        self.assertEquals(list(entry.itervalues()), [
            "dc=example,dc=org", "bar1", "bar2", "bear"
        ])
        self.assertEquals(list(entry.iteritems()), [
            ('dn', "dc=example,dc=org", ), ('foo', "bar1"), ('foo', "bar2"),
            ('zoo', 'bear')
        ])
        self.assertEquals(len(entry), 4)

    def test_as_change_record(self):
        entry = Entry("dc=example,dc=org", {'dc': 'example', 'objectClass':
            'dcObject'})
        change = entry.as_change_record()
        self.assertEquals(change.dn, entry.dn)
        self.assertEquals(change.entry, entry)

    def test_apply_to_server(self):
        server = MockServer()
        entry = Entry("dc=example,dc=org", {'dc': 'example', 'objectClass':
            'dcObject'})
        entry.apply_to_server(server)
        self.assertEquals(server.calls, [('add', {
            'dn': "dc=example,dc=org",
            'modlist': [
                ('objectClass', ["dcObject"]),
                ('dc', ["example"]),
            ]
        })])

    def test_str(self):
        from urllib2 import urlopen
        from os.path import abspath
        url = "file:%s" % abspath(__file__)
        entry = Entry("dc=example,dc=org", {
            'dc': 'example', 'objectClass': ['dcObject', 'top'],
            'cn': u"\u5c0f\u7b20\u539f",'file': urlopen(url)
        })
        self.assertEquals(str(entry),
            "dn: dc=example,dc=org\n"
            "objectClass: dcObject\n"
            "objectClass: top\n"
            "dc: example\n"
            "file:< %s\n"
            "cn:: 5bCP56yg5Y6f\n" % url
        )

    def test_repr(self):
        entry = Entry("dc=example,dc=org", {
            'dc': "example",
            'objectClass': ["dcObject", "top"]
        })
        self.assertEquals(repr(entry), "Entry('dc=example,dc=org', "
            "{'objectClass': ['dcObject', 'top'], 'dc': ['example']})"
        )


class AddChangeRecordTestCase(unittest.TestCase):

    def setUp(self):
        self.entry = Entry("dc=example,dc=org", {
            'dc': "example",
            'objectClass': ["dcObject", "top"]
        })
        self.record = AddChangeRecord(self.entry)

    def test_create(self):
        self.assertEquals(self.record.dn, "dc=example,dc=org")
        self.assertEquals(self.record.entry, self.entry)

    def test_attrvals(self):
        self.assertEquals(self.record._attrvals(), (
            ('dn', "dc=example,dc=org"),
            ('changetype', "add"),
            ('objectClass', "dcObject"),
            ('objectClass', "top"),
            ('dc', "example"),
        ))

    def test_apply_to_server(self):
        server = MockServer()
        self.record.apply_to_server(server)
        self.assertEquals(server.calls, [('add', {
            'dn': "dc=example,dc=org",
            'modlist': [
                ('objectClass', ["dcObject", "top"]),
                ('dc', ['example']),
            ]
        })])


    def test_str(self):
        self.assertEquals(str(self.record),
            "dn: dc=example,dc=org\n"
            "changetype: add\n"
            "objectClass: dcObject\n"
            "objectClass: top\n"
            "dc: example\n"
        )

    def test_repr(self):
        self.assertEquals(repr(self.record), "AddChangeRecord(Entry("
            "'dc=example,dc=org', {'objectClass': ['dcObject', 'top'], "
            "'dc': ['example']}))"
        ) 


class DeleteChangeRecordTestCase(unittest.TestCase):

    def test_create(self):
        record = DeleteChangeRecord("dc=example,dc=org")
        self.assertEquals(record.dn, "dc=example,dc=org")

    def test_attrvals(self):
        record = DeleteChangeRecord("dc=example,dc=org")
        self.assertEquals(record._attrvals(), (
            ('dn', "dc=example,dc=org"),
            ('changetype', "delete"),
        ))

    def test_apply_to_server(self):
        server = MockServer()
        record = DeleteChangeRecord("dc=example,dc=org")
        record.apply_to_server(server)
        self.assertEquals(server.calls, [
            ('delete', {'dn': "dc=example,dc=org"})
        ])

    def test_str(self):
        record = DeleteChangeRecord("dc=example,dc=org")
        self.assertEquals(str(record),
            "dn: dc=example,dc=org\n"
            "changetype: delete\n"
        )

    def test_repr(self):
        rec = DeleteChangeRecord("dc=example,dc=org")
        self.assertEquals(repr(rec), "DeleteChangeRecord('dc=example,dc=org')")


class RenameChangeRecordTestCase(unittest.TestCase):

    def test_init_args(self):
        self.assertEquals(getargspec(RenameChangeRecord.__init__), (['self',
            'dn', 'newrdn', 'delete', 'newsuperior'], None, None, (True, None))
        )

    def test_attrvals(self):
        record = RenameChangeRecord(
            "cn=Paul Jensen,ou=Product Development,dc=airius,dc=com",
            "cn=Paula Jensen",
        )
        self.assertEquals(record._attrvals(), (
            ('dn',"cn=Paul Jensen,ou=Product Development,dc=airius,dc=com"),
            ('changetype', "modrdn"),
            ('newrdn', "cn=Paula Jensen"),
            ('deleteoldrdn', 1),
        ))
        record = RenameChangeRecord(
            "ou=PD Accountants,ou=Product Development,dc=airius,dc=com",
            "ou=Product Development Accountants",
            False,
            "ou=Accounting,dc=airius,dc=com"
        )
        self.assertEquals(record._attrvals(), (
            ('dn',"ou=PD Accountants,ou=Product Development,dc=airius,dc=com"),
            ('changetype', "modrdn"),
            ('newrdn', "ou=Product Development Accountants"),
            ('deleteoldrdn', 0),
            ('newsuperior', "ou=Accounting,dc=airius,dc=com"),
        ))

    def test_apply_to_server(self):
        server = MockServer()
        record = RenameChangeRecord(
            "cn=Paul Jensen,ou=Product Development,dc=airius,dc=com",
            "cn=Paula Jensen",
        )
        record.apply_to_server(server)
        self.assertEquals(server.calls, [('rename', {
            'dn': "cn=Paul Jensen,ou=Product Development,dc=airius,dc=com",
            'newrdn': "cn=Paula Jensen",
            'newsuperior': None,
            'delete': True,
        })])


def test_str(self):
    record = RenameChangeRecord(
        "cn=Paul Jensen,ou=Product Development,dc=airius,dc=com",
        "cn=Paula Jensen",
    )
    self.assertEquals(str(record),
        "dn: cn=Paul Jensen,ou=Product Development,dc=airius,dc=com\n"
        "changetype: modrdn\n"
        "newrdn: cn=Paula Jensen\n"
        "deleteoldrdn: 1\n"
    )

def test_repr(self):
    record = RenameChangeRecord(
        "cn=Paul Jensen,ou=Product Development,dc=airius,dc=com",
        "cn=Paula Jensen",
    )
    self.assertEquals(repr(record), "RenameChangeRecord('cn=Paul Jensen,"
        "ou=Product Development,dc=airius,dc=com', 'cn=Paula Jensen', True,"
        " None)"
    )


class ModifyChangeRecordTestCase(unittest.TestCase):

    def test_create(self):
        record = ModifyChangeRecord("dc=example,dc=org")
        self.assertEquals(record.dn, "dc=example,dc=org")

    def test_attrvals(self):
        record = ModifyChangeRecord("dc=example,dc=org")
        record.add('attr1', 'val1')
        record.add('attr1', 'val2')
        record.add('attr2', ['val3','val4'])
        record.delete('attr3', 'val5')
        record.delete('attr4')
        record.replace('attr5', ['val6', 'val7', 'val8'])
        record.replace('attr6')
        attrvals = record._attrvals()
        self.assertEquals(len(attrvals), 9)
        self.assertEquals(attrvals[0], ('dn', "dc=example,dc=org"))
        self.assertEquals(attrvals[1], ('changetype', "modify"))
        self.assertEquals(attrvals[2]._attrvals(), (
            ('add', "attr1"),
            ('attr1', "val1"),
        ))
        self.assertEquals(attrvals[3]._attrvals(), (
            ('add', "attr1"),
            ('attr1', "val2"),
        ))
        self.assertEquals(attrvals[4]._attrvals(), (
            ('add', "attr2"),
            ('attr2', "val3"),
            ('attr2', "val4"),
        ))
        self.assertEquals(attrvals[5]._attrvals(), (
            ('delete', "attr3"),
            ('attr3', "val5"),
        ))
        self.assertEquals(attrvals[6]._attrvals(), (
            ('delete', "attr4"),
        ))
        self.assertEquals(attrvals[7]._attrvals(), (
            ('replace', "attr5"),
            ('attr5', "val6"),
            ('attr5', "val7"),
            ('attr5', "val8"),
        ))
        self.assertEquals(attrvals[8]._attrvals(), (
            ('replace', "attr6"),
        ))


    def test_apply_to_server(self):
        server = MockServer()
        record = ModifyChangeRecord("dc=example,dc=org")
        record.add('attr1', 'val1')
        record.add('attr1', 'val2')
        record.add('attr2', ['val3','val4'])
        record.delete('attr3', 'val5')
        record.delete('attr4')
        record.replace('attr5', ['val6', 'val7', 'val8'])
        record.replace('attr6')
        record.apply_to_server(server)
        self.assertEquals(server.calls, [('modify', {
            'dn': "dc=example,dc=org",
            'modlist': [
                (Server.MOD_ADD, 'attr1', ['val1']),
                (Server.MOD_ADD, 'attr1', ['val2']),
                (Server.MOD_ADD, 'attr2', ['val3', 'val4']),
                (Server.MOD_DELETE, 'attr3', ['val5']),
                (Server.MOD_DELETE, 'attr4', []),
                (Server.MOD_REPLACE, 'attr5', ['val6','val7','val8']),
                (Server.MOD_REPLACE, 'attr6', []),
            ]
        })])

    def test_str(self):
        record = ModifyChangeRecord("dc=example,dc=org")
        record.add('attr1', 'val1')
        record.add('attr1', 'val2')
        record.add('attr2', ['val3','val4'])
        record.delete('attr3', 'val5')
        record.delete('attr4')
        record.replace('attr5', ['val6', 'val7', 'val8'])
        record.replace('attr6')
        self.assertEquals(str(record),
            "dn: dc=example,dc=org\n"
            "changetype: modify\n"
            "add: attr1\n"
            "attr1: val1\n"
            "-\n"
            "add: attr1\n"
            "attr1: val2\n"
            "-\n"
            "add: attr2\n"
            "attr2: val3\n"
            "attr2: val4\n"
            "-\n"
            "delete: attr3\n"
            "attr3: val5\n"
            "-\n"
            "delete: attr4\n"
            "-\n"
            "replace: attr5\n"
            "attr5: val6\n"
            "attr5: val7\n"
            "attr5: val8\n"
            "-\n"
            "replace: attr6\n"
            "-\n"
        )

    def test_repr(self):
        record = ModifyChangeRecord("dc=example,dc=org")
        record.add('attr1', 'val1')
        record.add('attr1', 'val2')
        record.add('attr2', ['val3','val4'])
        record.delete('attr3', 'val5')
        record.delete('attr4')
        record.replace('attr5', ['val6', 'val7', 'val8'])
        record.replace('attr6')
        self.assertEquals(repr(record),
            "ModifyChangeRecord('dc=example,dc=org', ["
            "AddModification('attr1', ['val1']), "
            "AddModification('attr1', ['val2']), "
            "AddModification('attr2', ['val3', 'val4']), "
            "DeleteModification('attr3', ['val5']), "
            "DeleteModification('attr4', []), "
            "ReplaceModification('attr5', ['val6', 'val7', 'val8']), "
            "ReplaceModification('attr6', [])"
            "])"
        )


class RecordListTestCase(unittest.TestCase):

    def setUp(self):
        self.list = RecordList()
        self.list.append(DeleteChangeRecord("cn=foo,dc=example,dc=org"))
        self.list.append(DeleteChangeRecord("cn=bar,dc=example,dc=org"))
        self.list.append(Entry("cn=moo,dc=example,dc=org"))

    def test_create(self):
        self.assertEquals(len(self.list), 3)
        self.assert_(isinstance(self.list[0], DeleteChangeRecord))
        self.assert_(isinstance(self.list[1], DeleteChangeRecord))
        self.assert_(isinstance(self.list[2], Entry))
        self.assert_(self.list[0].dn == "cn=foo,dc=example,dc=org")
        self.assert_(self.list[1].dn == "cn=bar,dc=example,dc=org")
        self.assert_(self.list[2].dn == "cn=moo,dc=example,dc=org")

    def test_apply_to_server(self):
        server = MockServer()
        self.list.apply_to_server(server)
        self.assertEquals(server.calls, [
            ('delete', {'dn': "cn=foo,dc=example,dc=org"}),
            ('delete', {'dn': "cn=bar,dc=example,dc=org"}),
            ('add', {'dn': "cn=moo,dc=example,dc=org", 'modlist': []}),
        ])

    def test_str(self):
        self.assertEquals(str(self.list),
            "version: 1\n"
            "\n"
            "dn: cn=foo,dc=example,dc=org\n"
            "changetype: delete\n"
            "\n"
            "dn: cn=bar,dc=example,dc=org\n"
            "changetype: delete\n"
            "\n"
            "dn: cn=moo,dc=example,dc=org\n"
            "changetype: add\n"
            "\n"
        )

    def test_repr(self):
        self.assertEquals(repr(self.list), "RecordList(DeleteChangeRecord('cn=f"
            "oo,dc=example,dc=org'), DeleteChangeRecord('cn=bar,dc=example,dc=o"
            "rg'), Entry('cn=moo,dc=example,dc=org', {}))"
        )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SafeStringTestCase))
    suite.addTest(unittest.makeSuite(ServerTestCase))
    suite.addTest(unittest.makeSuite(AttrValContainerTestCase))
    suite.addTest(unittest.makeSuite(EntryTestCase))
    suite.addTest(unittest.makeSuite(AddChangeRecordTestCase))
    suite.addTest(unittest.makeSuite(DeleteChangeRecordTestCase))
    suite.addTest(unittest.makeSuite(RenameChangeRecordTestCase))
    suite.addTest(unittest.makeSuite(ModifyChangeRecordTestCase))
    suite.addTest(unittest.makeSuite(RecordListTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')

