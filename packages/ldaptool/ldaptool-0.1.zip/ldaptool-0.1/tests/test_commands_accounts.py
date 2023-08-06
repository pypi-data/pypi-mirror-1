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

from ldaptool.ldap import RecordList, Server, Entry, DeleteChangeRecord
from ldaptool.accounts import Group
from ldaptool.settings import Settings
from ldaptool.commands.accounts import *


class MockServer(Server):
    
    def __init__(self, uri=None):
        self.uri = uri
        self.instructions = []

    def search(self, *args, **kwargs):
        self.instructions.append(('search', args, kwargs)) 
        if (args, kwargs) == ((), {'scope': 0,
            'base': 'cn=group1,ou=Groups,dc=example,dc=org',
            'filter': '(objectClass=posixGroup)', 'size_limit': 1}):
            return [Entry('cn=group1,ou=Groups,dc=example,dc=org', {
                'cn': 'group1',
                'gidNumber': '1',
                'objectClass': ['top', 'posixGroup'],
            })]
        if (args, kwargs) == ((), {'scope': 2, 'base': 'dc=example,dc=org',
            'filter': '(&(objectClass=posixGroup)(cn=group2))',
            'size_limit': 1}):
            return [Entry('cn=group2,ou=Groups,dc=example,dc=org', {
                'cn': 'group2',
                'gidNumber': '2',
                'objectClass': ['top', 'posixGroup'],
            })]
        if (args, kwargs) == ((), {'scope': 2, 'base': 'dc=example,dc=org',
            'filter': '(&(objectClass=posixGroup)(gidNumber=3))',
            'size_limit': 1}):
            return [Entry('cn=group3,ou=Groups,dc=example,dc=org', {
                'cn': 'group3',
                'gidNumber': '3',
                'objectClass': ['top', 'posixGroup'],
            })]
        if (args, kwargs) == ((), {'scope': 2, 'base': 'dc=example,dc=org',
            'filter': '(&(objectClass=posixGroup)(gidNumber=4))',
            'size_limit': 1}):
            return [Entry('cn=group4,ou=Groups,dc=example,dc=org', {
                'cn': 'group4',
                'gidNumber': '4',
                'objectClass': ['top', 'posixGroup'],
            })]
        if (args, kwargs) == ((), {'filter': '(objectClass=posixGroup)',
            'scope': 2, 'base': 'dc=example,dc=org', 'attr_list':
            ['gidNumber']}):
            return [
                Entry("cn=group1,ou=Groups,dc=example,dc=org",
                    {'gidNumber': "1"}),
                Entry("cn=group2,ou=Groups,dc=example,dc=org",
                    {'gidNumber': "2"}),
                Entry("cn=group3,ou=Groups,dc=example,dc=org",
                    {'gidNumber': "3"}),
                Entry("cn=group4,ou=Groups,dc=example,dc=org",
                    {'gidNumber': "4"}),
                Entry("cn=group7,ou=Groups,dc=example,dc=org",
                    {'gidNumber': "7"}),
            ]
        if (args, kwargs) == ((), {'filter':
            '(&(objectClass=posixAccount)(uid=user1))', 'scope': 2, 'base':
            'dc=example,dc=org', 'size_limit': 1}):
            return [Entry("uid=user1,ou=Users,dc=example,dc=org", {
                'uid': "user1",
                'uidNumber': "1",
                'cn': "Doe, John",
                'surname': "Doe",
                'givenName': "Joe",
            })]
        if (args, kwargs) == ((), {'filter': '(objectClass=posixAccount)',
            'scope': 2, 'base': 'dc=example,dc=org', 'attr_list':
            ['uidNumber']}):
            return [
                Entry("cn=user1,ou=Users,dc=example,dc=org",
                    {'uidNumber': "1"}),
                Entry("cn=user2,ou=Users,dc=example,dc=org",
                    {'uidNumber': "2"}),
                Entry("cn=user3,ou=Users,dc=example,dc=org",
                    {'uidNumber': "3"}),
                Entry("cn=user4,ou=Users,dc=example,dc=org",
                    {'uidNumber': "4"}),
                Entry("cn=user7,ou=Users,dc=example,dc=org",
                    {'uidNumber': "7"}),
            ]
        if (args, kwargs) == ((), {'scope': 2, 'base': 'dc=example,dc=org',
            'filter': '(&(objectClass=posixAccount)(uidNumber=4))',
            'size_limit': 1}):
            return [Entry('uid=user4,ou=Users,dc=example,dc=org', {
                'uid': 'user4',
                'uidNumber': '4',
                'objectClass': ['top', 'posixAccount'],
            })]
        return []

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


class AccountCommandTestCase(unittest.TestCase):

    def test_fix_settings(self):
        command = AccountCommand(Settings())
        settings = command.settings
        self.assertEquals(
            settings['USER_DN'],
            "uid=%(user)s,ou=Users,%(basedn)s"
        )
        self.assertEquals(
            settings['GROUP_DN'],
            "cn=%(group)s,ou=Groups,%(basedn)s"
        )
        self.assertEquals(settings['POSIX_GROUP_MODE'], True)
        self.assertEquals(settings['GROUP_MEMBER_FIELD'], "memberUid")

    def test_is_dn(self):
        command = AccountCommand(Settings())
        self.assertTrue(command.is_dn("cn=foo,dc=example,dc=org"))
        self.assertFalse(command.is_dn("foo"))

    def test_get_user_dn(self):
        # Test with default USER_DN
        command = AccountCommand(Settings(
            LDAP_BASE="ou=tests,dc=example,dc=org"
        ))
        self.assertEquals(
            command.get_user_dn("uid=foo,dc=example,dc=org"),
            "uid=foo,dc=example,dc=org"
        )
        self.assertEquals(
            command.get_user_dn("foo"),
            command.settings['USER_DN'] % {
                'user': "foo",
                'basedn': "ou=tests,dc=example,dc=org"
            }
        )
        # Test with explicit USER_DN
        command = AccountCommand(Settings(
            LDAP_BASE="ou=tests,dc=example,dc=org",
            USER_DN="uid=%(user)s,cn=%(group)s,%(basedn)s"
        ))
        self.assertEquals(
            command.get_user_dn("uid=foo,dc=example,dc=org"),
            "uid=foo,dc=example,dc=org"
        )
        self.assertEquals(
            command.get_user_dn("foo", {'group': "bar"}),
            "uid=foo,cn=bar,ou=tests,dc=example,dc=org"
        )
        self.assertRaises(KeyError, command.get_user_dn, "foo")

    def test_get_group_dn(self):
        # Test with default GROUP_DN
        command = AccountCommand(Settings(
            LDAP_BASE="ou=tests,dc=example,dc=org"
        ))
        self.assertEquals(
            command.get_group_dn("cn=foo,dc=example,dc=org"),
            "cn=foo,dc=example,dc=org"
        )
        self.assertEquals(
            command.get_group_dn("foo"),
            command.settings['GROUP_DN'] % {
                'group': "foo",
                'basedn': "ou=tests,dc=example,dc=org"
            }
        )
        # Test with explicit GROUP_DN
        command = AccountCommand(Settings(
            LDAP_BASE="ou=tests,dc=example,dc=org",
            GROUP_DN="cn=%(group)s,%(basedn)s"
        ))
        self.assertEquals(
            command.get_group_dn("cn=foo,dc=example,dc=org"),
            "cn=foo,dc=example,dc=org"
        )
        self.assertEquals(
            command.get_group_dn("foo"),
            "cn=foo,ou=tests,dc=example,dc=org"
        )


class UseraddTestCase(unittest.TestCase):

    def test_fix_settings(self):
        useradd = Useradd(Settings())
        settings = useradd.settings
        self.assertEquals(settings['UID_MIN'], 1000)
        self.assertEquals(settings['UID_MAX'], 60000)
        self.assertEquals(settings['SHELL'], "/bin/bash")
        self.assertEquals(settings['HOME'], "/home/%(user)s")

    def test_fix_params_user(self):
        useradd = Useradd(Settings(
            LDAP_BASE="dc=example,dc=org",
            USER_DN="uid=%(user)s,ou=Users,%(basedn)s"
        ))
        # Must specify user to add
        try:
            useradd._fix_params([], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Wrong number of arguments")
        # Username required when specifying distinguished name
        try:
            useradd._fix_params(["uid=user1,dc=example,dc=org"], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Username must be supplied when using "
                "a distinguished name as the user argument.")
        args = ["uid=user1,dc=example,dc=org"]
        kwargs = {'user': "user1"}
        useradd._fix_params(args, kwargs)
        self.assertEquals(args, ["uid=user1,dc=example,dc=org"])
        self.assertEquals(kwargs['user'], "user1")
        # Username implicitly declared when not using distinguished name
        args = ["user1"]
        kwargs = {}
        useradd._fix_params(args, kwargs)
        self.assertEquals(args, ["uid=user1,ou=Users,dc=example,dc=org"])
        self.assertEquals(kwargs['user'], "user1")
        # But should not override when explicitely set
        args = ["user1"]
        kwargs = {'user': "foo"}
        useradd._fix_params(args, kwargs)
        self.assertEquals(args, ["uid=user1,ou=Users,dc=example,dc=org"])
        self.assertEquals(kwargs['user'], "foo")

    def test_fix_params_groups(self):
        useradd = Useradd(Settings())
        useradd.server = MockServer()
        # No group, no suplemental groups
        args, kwargs = (["user1"], {})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['group'], None)
        self.assertEquals(kwargs['groups'], [])
        self.assertEquals(len(useradd.server.instructions), 0)
        # Specified group, no suplemental groups
        args, kwargs = (["user1"], {'group': "group2"})
        useradd._fix_params(args, kwargs)
        self.assertEquals(type(kwargs['group']), Entry)
        self.assertEquals(kwargs['group'].dn,
            "cn=group2,ou=Groups,dc=example,dc=org"
        )
        self.assertEquals(kwargs['groups'], [])
        self.assertEquals(len(useradd.server.instructions), 1)
        # Specified group, suplemental groups
        useradd.server = MockServer()
        args, kwargs = (["user1"], {'group': "group2", 'groups': [
            "cn=group1,ou=Groups,dc=example,dc=org", "3"]})
        useradd._fix_params(args, kwargs)
        self.assertEquals(type(kwargs['group']), Entry)
        self.assertEquals(kwargs['group'].dn,
            "cn=group2,ou=Groups,dc=example,dc=org")
        self.assertEquals(len(kwargs['groups']), 2)
        self.assertEquals(kwargs['groups'][0].dn,
            "cn=group1,ou=Groups,dc=example,dc=org")
        self.assertEquals(kwargs['groups'][1].dn,
            "cn=group3,ou=Groups,dc=example,dc=org")
        self.assertEquals(len(useradd.server.instructions), 3)
        # No group, specified suplemental groups
        useradd.server = MockServer()
        args, kwargs = (["user1"], {
            'groups': ["cn=group1,ou=Groups,dc=example,dc=org", "3"]
        })
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['group'], None)
        self.assertEquals(len(kwargs['groups']), 2)
        self.assertEquals(kwargs['groups'][0].dn,
            "cn=group1,ou=Groups,dc=example,dc=org")
        self.assertEquals(kwargs['groups'][1].dn,
            "cn=group3,ou=Groups,dc=example,dc=org")
        self.assertEquals(len(useradd.server.instructions), 2)
        # Unknown groups
        try:
            useradd._fix_params(["user1"], {'group': "foo"})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "The group 'foo' does not exist")
        try:
            useradd._fix_params(["user1"], {'groups': ["group2", "foo"]})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "The group 'foo' does not exist")

    def test_fix_params_uid(self):
        useradd = Useradd(Settings())
        args, kwargs = (["user1"], {})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['uid'], None)
        args, kwargs = (["user1"], {'uid': 1000})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['uid'], 1000)
        args, kwargs = (["user1"], {'uid': "1000"})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['uid'], 1000)
        args, kwargs = (["user1"], {'uid': "foo"})
        try:
            useradd._fix_params(args, kwargs)
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Invalid UID 'foo'")

    def test_fix_params_names(self):
        useradd = Useradd(Settings())
        args, kwargs = (["user1"], {})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['user'], "user1")
        self.assertEquals(kwargs['name'], "user1")
        self.assertEquals(kwargs['surname'], "user1")
        self.assertEquals(kwargs['firstname'], None)
        args, kwargs = (["user1"], {'name': "Doe"})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['user'], "user1")
        self.assertEquals(kwargs['name'], "Doe")
        self.assertEquals(kwargs['surname'], "Doe")
        self.assertEquals(kwargs['firstname'], None)
        args, kwargs = (["user1"], {'name': "Doe , John"})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['user'], "user1")
        self.assertEquals(kwargs['name'], "Doe , John")
        self.assertEquals(kwargs['surname'], "Doe")
        self.assertEquals(kwargs['firstname'], "John")

    def test_fix_params_others(self):
        useradd = Useradd(Settings(HOME="/home/%(user)s", SHELL="/bin/bash"))
        args, kwargs = (["user1"], {})
        useradd._fix_params(args, kwargs)
        self.assertEquals(kwargs['comment'], None)
        self.assertEquals(kwargs['home'], "/home/%(user)s")
        self.assertEquals(kwargs['mail'], None)
        self.assertEquals(kwargs['unique'], True)
        self.assertEquals(kwargs['shell'], "/bin/bash")

    def test_create_ldif_username(self):
        useradd = Useradd(Settings())
        useradd.server = MockServer()
        # Fail on non-unique username
        args = [ "uid=user1,ou=Users,dc=example,dc=org" ]
        kwargs = {'user': "user1"}
        useradd._fix_params(args, kwargs)
        try:
            useradd.create_ldif(*args, **kwargs)
            print useradd.server.instructions
            self.fail("Failed to raise ValueError.")
        except ValueError, e:
            self.assertEquals(e.message, "User user1 already exists")

    def test_create_ldif_uid(self):
        useradd = Useradd(Settings(UID_MIN=1, UID_MAX=10))
        useradd.server = MockServer()
        # Get a free GID
        args = [ "cn=user2,ou=Users,dc=example,dc=org" ]
        kwargs = {'user': "user2", 'group': "group2"}
        useradd._fix_params(args, kwargs)
        ldif = useradd.create_ldif(*args, **kwargs)
        self.assertEquals(len(ldif), 1)
        self.assertEquals(ldif[0].uidNumber, ["8"])
        # Fail on existing UID
        args = [ "uid=user2,ou=Users,dc=example,dc=org" ]
        kwargs = {'user': "user2", 'unique': True, 'group': "group2", 'uid': 4}
        useradd._fix_params(args, kwargs)
        try:
            useradd.create_ldif(*args, **kwargs)
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "UID 4 is not unique")
        # Succeed on existing UID but non-unique.
        args = [ "uid=user2,ou=Users,dc=example,dc=org" ]
        kwargs = {'user': "user2", 'unique': False, 'group': "group2", 'uid': 4}
        useradd._fix_params(args, kwargs)
        ldif = useradd.create_ldif(*args, **kwargs)
        self.assertEquals(len(ldif), 1)
        self.assertEquals(ldif[0].uidNumber, ["4"])

    def test_create_ldif_group(self):
        useradd = Useradd(Settings(
            GID_MIN=1, GID_MAX=10,
            UID_MIN=1, UID_MAX=10
        ))
        useradd.server = MockServer()
        # Determine gidNumber from specified group
        args, kwargs = (["user8"], {'group': 'group2', 'uid': 8})
        useradd._fix_params(args, kwargs)
        ldif = useradd.create_ldif(*args, **kwargs)
        self.assertEquals(len(ldif), 1)
        self.assertEquals(ldif[0].uidNumber, ["8"])
        self.assertEquals(ldif[0].gidNumber, ["2"])
        # Create corresponding group
        args, kwargs = (["user8"], {'group': None, 'uid': 8})
        useradd._fix_params(args, kwargs)
        ldif = useradd.create_ldif(*args, **kwargs)
        self.assertEquals(len(ldif), 2)
        self.assertEquals(ldif[0].gidNumber, ["8"])
        self.assertEquals(ldif[0].cn, ["user8"])
        self.assertEquals(ldif[1].uidNumber, ["8"])
        self.assertEquals(ldif[1].uid, ["user8"])
        # TODO add a test where the selected user UID or user name is still
        # available, but the corresponding GID or group name is not.

    def test_create_ldif_supplemental_groups(self):
        useradd = Useradd(Settings())
        useradd.server = MockServer()
        args, kwargs = (["user8"], {
            'uid': 8,
            'group':
            "group2",
            'groups': [
                'cn=group1,ou=Groups,dc=example,dc=org',
                'group2', "3", 4
            ]
        })
        useradd._fix_params(args, kwargs)
        ldif = useradd.create_ldif(*args, **kwargs)
        self.assertEquals(len(ldif), 5)
        self.assertEquals(ldif[0].uid, ["user8"])
        self.assertEquals(ldif[0].uidNumber, ["8"])
        # TODO test that the change records are correct. Do this also for
        # non POSIX_GROUP_MODE and a different GROUP_MEMBER_FIELD
        self.assertEquals(ldif[1].dn, 'cn=group1,ou=Groups,dc=example,dc=org')
        self.assertEquals(ldif[2].dn, 'cn=group2,ou=Groups,dc=example,dc=org')
        self.assertEquals(ldif[3].dn, 'cn=group3,ou=Groups,dc=example,dc=org')
        self.assertEquals(ldif[4].dn, 'cn=group4,ou=Groups,dc=example,dc=org')

    def test_create_ldif_others(self):
        # TODO Check boring parameters such as e-mail and comments
        pass


class GroupaddTestCase(unittest.TestCase):

    def test_fix_settings(self):
        groupadd = Groupadd(Settings())
        settings = groupadd.settings
        self.assertEquals(settings['GID_MIN'], 100)
        self.assertEquals(settings['GID_MAX'], 60000)
        self.assertRaises(ValueError, Groupadd, Settings(GID_MIN=2,GID_MAX=1))

    def test_fix_params_group(self):
        groupadd = Groupadd(Settings(
            LDAP_BASE="dc=example,dc=org",
            GROUP_DN="cn=%(group)s,ou=Groups,%(basedn)s"
        ))
        # Must specify group to add
        try:
            groupadd._fix_params([], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Wrong number of arguments")
        # Group name required when specifying distinguished name
        try:
            groupadd._fix_params(["cn=group1,dc=example,dc=org"], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Group name must be supplied when "
                "using a distinguished name as the group argument.")
        args = ["cn=group1,dc=example,dc=org"]
        kwargs = {'group': "group1"}
        groupadd._fix_params(args, kwargs)
        self.assertEquals(args, ["cn=group1,dc=example,dc=org"])
        self.assertEquals(kwargs['group'], "group1")
        # Username implicitly declared when not using distinguished name
        args = ["group1"]
        kwargs = {}
        groupadd._fix_params(args, kwargs)
        self.assertEquals(args, ["cn=group1,ou=Groups,dc=example,dc=org"])
        self.assertEquals(kwargs['group'], "group1")
        # But should not override when explicitely set
        args = ["group1"]
        kwargs = {'group': "foo"}
        groupadd._fix_params(args, kwargs)
        self.assertEquals(args, ["cn=group1,ou=Groups,dc=example,dc=org"])
        self.assertEquals(kwargs['group'], "foo")

    def test_fix_params_gid(self):
        groupadd = Groupadd(Settings())
        args, kwargs = (["group1"], {})
        groupadd._fix_params(args, kwargs)
        self.assertEquals(kwargs['gid'], None)
        args, kwargs = (["group1"], {'gid': 1000})
        groupadd._fix_params(args, kwargs)
        self.assertEquals(kwargs['gid'], 1000)
        args, kwargs = (["group1"], {'gid': "1000"})
        groupadd._fix_params(args, kwargs)
        self.assertEquals(kwargs['gid'], 1000)
        args, kwargs = (["group1"], {'gid': "foo"})
        try:
            groupadd._fix_params(args, kwargs)
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Invalid GID 'foo'")

    def test_fix_params_others(self):
        groupadd = Groupadd(Settings())
        args, kwargs = (["group1"], {})
        groupadd._fix_params(args, kwargs)
        self.assertEquals(kwargs['comment'], None)
        self.assertEquals(kwargs['unique'], True)

    def test_first_free_gid(self):
        groupadd = Groupadd(Settings(GID_MIN=1, GID_MAX=10))
        groupadd.server = MockServer()
        self.assertEquals(groupadd.first_free_gid(), 8)
        groupadd = Groupadd(Settings(GID_MIN=10, GID_MAX=20))
        groupadd.server = MockServer()
        self.assertEquals(groupadd.first_free_gid(), 10)
        groupadd = Groupadd(Settings(GID_MIN=1, GID_MAX=4))
        groupadd.server = MockServer()
        try:
            groupadd.first_free_gid()
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "No free GIDs available")
        groupadd = Groupadd(Settings(GID_MIN=1, GID_MAX=7))
        groupadd.server = MockServer()
        try:
            groupadd.first_free_gid()
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "No free GIDs available")

    def test_is_free_gid(self):
        groupadd = Groupadd(Settings())
        groupadd.server = MockServer()
        self.assertTrue(groupadd.is_free_gid(2))
        self.assertFalse(groupadd.is_free_gid(3))

    def test_create_ldif(self):
        groupadd = Groupadd(Settings(GID_MIN=1, GID_MAX=10))
        groupadd.server = MockServer()
        args = [ "cn=group1,ou=Groups,dc=example,dc=org" ]
        kwargs = {'group': "group1", 'gid': 1000, 'comment': "the comment"}
        groupadd._fix_params(args, kwargs)
        ldif = groupadd.create_ldif(*args, **kwargs)
        self.assertEquals(type(ldif), RecordList)
        self.assertEquals(len(ldif), 1)
        ldif = ldif[0]
        self.assertEquals(type(ldif), Group)
        self.assertEquals(ldif.dn, "cn=group1,ou=Groups,dc=example,dc=org")
        self.assertEquals(ldif.attrs, {
            'cn': ["group1"],
            'gidNumber': ["1000"],
            'description': ["the comment"],
            'objectClass': ["posixGroup", "top"]
        })

    def test_create_ldif_group(self):
        groupadd = Groupadd(Settings())
        groupadd.server = MockServer()
        # Fail on non-unique group name
        args = [ "cn=group1,ou=Groups,dc=example,dc=org" ]
        kwargs = {'group': "group2"}
        groupadd._fix_params(args, kwargs)
        try:
            groupadd.create_ldif(*args, **kwargs)
            self.fail("Failed to raise ValuError.")
        except ValueError, e:
            self.assertEquals(e.message, "Group group2 already exists")

    def test_create_ldif_gid(self):
        groupadd = Groupadd(Settings(GID_MIN=1, GID_MAX=10))
        groupadd.server = MockServer()
        # Get a free GID
        args = [ "cn=group1,ou=Groups,dc=example,dc=org" ]
        kwargs = {'group': "group1"}
        groupadd._fix_params(args, kwargs)
        ldif = groupadd.create_ldif(*args, **kwargs)
        self.assertEquals(len(ldif), 1)
        self.assertEquals(ldif[0].gidNumber, ["8"])
        # Fail on existing GID
        args = [ "cn=group1,ou=Groups,dc=example,dc=org" ]
        kwargs = {'group': "group1", 'unique': True, 'gid': 4}
        groupadd._fix_params(args, kwargs)
        try:
            groupadd.create_ldif(*args, **kwargs)
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "GID 4 is not unique")
        # Succeed on existing GID but non-unique.
        args = [ "cn=group1,ou=Groups,dc=example,dc=org" ]
        kwargs = {'group': "group1", 'unique': False, 'gid': 4}
        groupadd._fix_params(args, kwargs)
        ldif = groupadd.create_ldif(*args, **kwargs)
        self.assertEquals(len(ldif), 1)
        self.assertEquals(ldif[0].gidNumber, ["4"])


class UserdelTestCase(unittest.TestCase):

    def test_fix_params(self):
        userdel = Userdel(Settings())
        userdel.server = MockServer()
        try:
            userdel._fix_params([], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Wrong number of arguments")
        try:
            userdel._fix_params(["foo"], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "The user 'foo' does not exist")
        args, kwargs = (["user1"], {})
        userdel.server = MockServer()
        userdel._fix_params(args, kwargs)
        self.assertEquals(type(args[0]), Entry)
        self.assertEquals(args[0].dn, "uid=user1,ou=Users,dc=example,dc=org")

    def test_create_ldif(self):
        userdel = Userdel(Settings())
        userdel.server = MockServer()
        args = ["user1"]
        userdel._fix_params(args, {})
        ldif = userdel.create_ldif(*args)
        self.assertEquals(len(ldif), 1)
        ldif = ldif[0]
        self.assertEquals(type(ldif), DeleteChangeRecord)
        self.assertEquals(ldif.dn, "uid=user1,ou=Users,dc=example,dc=org")


class GroupdelTestCase(unittest.TestCase):

    def test_fix_params(self):
        groupdel = Groupdel(Settings())
        groupdel.server = MockServer()
        try:
            groupdel._fix_params([], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "Wrong number of arguments")
        try:
            groupdel._fix_params(["foo"], {})
            self.fail("Failed to raise ValueError")
        except ValueError, e:
            self.assertEquals(e.message, "The group 'foo' does not exist")
        args, kwargs = (["group2"], {})
        groupdel.server = MockServer()
        groupdel._fix_params(args, kwargs)
        self.assertEquals(type(args[0]), Entry)
        self.assertEquals(args[0].dn, "cn=group2,ou=Groups,dc=example,dc=org")

    def test_create_ldif(self):
        groupdel = Groupdel(Settings())
        groupdel.server = MockServer()
        args = ["group2"]
        groupdel._fix_params(args, {})
        ldif = groupdel.create_ldif(*args)
        self.assertEquals(len(ldif), 1)
        ldif = ldif[0]
        self.assertEquals(type(ldif), DeleteChangeRecord)
        self.assertEquals(ldif.dn, "cn=group2,ou=Groups,dc=example,dc=org")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AccountCommandTestCase))
    suite.addTest(unittest.makeSuite(UseraddTestCase))
    suite.addTest(unittest.makeSuite(GroupaddTestCase))
    suite.addTest(unittest.makeSuite(UserdelTestCase))
    suite.addTest(unittest.makeSuite(GroupdelTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')

