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

"""Commands for manipulating accounts."""

from ldaptool.commands.console import LdapCommand
from ldaptool.util import ugettext as _
from ldaptool.util import is_intlike
from ldaptool.settings import Settings
from ldaptool.ldap import Server, RecordList, Entry, ModifyChangeRecord, \
    DeleteChangeRecord
from ldaptool.accounts import User, Group


__all__ = ('AccountCommand', 'Useradd', 'Groupadd', 'Userdel', 'Groupdel')


class AccountCommand(LdapCommand):
    """Abstract superclass for commands that manipulate accounts."""

    def is_dn(self, string):
        """Return ``True`` if *string* looks like a distinguished name.
        
        As this is currently only used to distinguish simple user from
        distinguished names we only check for the presence of an equals sign '='
        in `string`.

        """
        return '=' in string

    def get_user_dn(self, string, kwargs=None):
        """Return a user distinguished name for *string*.

        If *string* already looks like a distinguished name it will simply be
        returned. If *string* looks more like a simple user name, it will be
        transformed into a distinguished name using the USER_DN configuration
        option and any other arguments passed in *kwargs*.

        """
        if self.is_dn(string):
            return string
        kwargs = dict(kwargs or {})
        kwargs['user'] = string
        return self.format_string(self.settings['USER_DN'], kwargs)

    def get_group_dn(self, string, kwargs=None):
        """Return a group distinguished name for *string*.

        If *string* already looks like a distinguished name it will simply be
        returned. If *string* looks more like a simple group name, it will be
        transformed into a distinguished name using the GROUP_DN configuration
        option and any other arguments passed in *kwargs*.

        """
        if self.is_dn(string):
            return string
        kwargs = dict(kwargs or {})
        kwargs['group'] = string
        return self.format_string(self.settings['GROUP_DN'], kwargs)

    def find_user(self, user):
        """Return the user for *user*.

        This searches the LDAP tree for the specified user. The parameter *user*
        can be the distinguished name, the uid number of the uid of the user.
        The method will try to detect the parameter and search accordingly.

        """
        kwargs = {}
        kwargs['base'] = self.settings['LDAP_BASE']
        kwargs['scope'] = Server.SCOPE_SUBTREE
        kwargs['size_limit'] = 1
        if isinstance(user, Entry):
            return user
        elif is_intlike(user):
            kwargs['filter'] = \
                "(&(objectClass=posixAccount)(uidNumber=%d))" % int(user)
        elif self.is_dn(user):
            kwargs['base'] = user
            kwargs['scope'] = Server.SCOPE_BASE
            kwargs['filter'] = "(objectClass=posixAccount)"
        else:
            kwargs['filter'] =  "(&(objectClass=posixAccount)(uid=%s))" % user
        results = self.server.search(**kwargs)
        if not results:
            return None
        return results[0]

    def find_group(self, group):
        """Return the group for *group*.

        This searches the LDAP tree for the specified group. The parameter
        *group* can be the distinguished name, the gid number of the common
        name of the group.  The method will try to detect the parameter and
        search accordingly.

        """
        kwargs = {}
        kwargs['base'] = self.settings['LDAP_BASE']
        kwargs['scope'] = Server.SCOPE_SUBTREE
        kwargs['size_limit'] = 1
        if isinstance(group, Entry):
            return group
        elif is_intlike(group):
            kwargs['filter'] = \
                "(&(objectClass=posixGroup)(gidNumber=%d))" % int(group)
        elif self.is_dn(group):
            kwargs['base'] = group
            kwargs['scope'] = Server.SCOPE_BASE
            kwargs['filter'] = "(objectClass=posixGroup)"
        else:
            kwargs['filter'] =  "(&(objectClass=posixGroup)(cn=%s))" % group
        results = self.server.search(**kwargs)
        if not results:
            return None
        return results[0]

    def _fix_settings(self, settings):
        super(AccountCommand, self)._fix_settings(settings)
        settings['USER_DN'] = settings.get('USER_DN') \
            or "uid=%(user)s,ou=Users,%(basedn)s"
        settings['GROUP_DN'] = settings.get('GROUP_DN') \
            or "cn=%(group)s,ou=Groups,%(basedn)s"
        settings['POSIX_GROUP_MODE'] = settings.get('POSIX_GROUP_MODE') != False
        settings['GROUP_MEMBER_FIELD'] = settings.get('GROUP_MEMBER_FIELD') \
            or "memberUid"

    def format_string(self, string, kwargs):
        d = {'basedn': self.settings['LDAP_BASE']}
        # Use values from kwargs if available
        if kwargs.get('group'): d['group'] = kwargs['group']
        if kwargs.get('user'): d['user'] = kwargs['user']
        if kwargs.get('uid'): d['uid'] = kwargs['uid']
        if kwargs.get('gid'): d['gid'] = kwargs['gid']
        # Convert Entry objects to strings
        if isinstance(d.get('user'), Entry):
            d['uid'] = d['user'].uidNumber[0]
            d['user'] = d['user'].uid[0]
        if isinstance(d.get('group'), Entry):
            d['gid'] = d['group'].gidNumber[0]
            d['group'] = d['group'].cn[0]
        return string % d


class Useradd(AccountCommand):
    """Command to create a new user."""

    @classmethod
    def name(cls):
        return 'useradd'

    def _init_option_parser(self, parser):
        parser.set_description(_("create a new user"))
        parser.add_argument('user')
        parser.add_option('-c', '--comment', help=_("Any text string. It can "
            "be used to specify a short description of the account."))
        parser.add_option('-d', '--home', help=_("The home directory of the "
            "user. The default is to the HOME setting as specified in the "
            "configuration file. Note that you must use a hook if you want the "
            "directory to be created for you."))
        parser.add_option('-g', '--group', '--gid', help=_("The group "
            "distinguished name, common name or number of the user's initial "
            "login group. The group name must exist. A group number must refer "
            "to an existing group. The default is to create a new group with "
            "the same name as the user's login name."))
        parser.add_option('-G', '--groups', type="list", help=_("A list of "
            "supplementary groups which the user is also a member of. Each "
            "group is separated from the next by a colon with no intervening "
            "whitespace. The groups are subject to the same restrictions as "
            "the group given with the -g option. The default is for the user "
            "to belong to no supplementary groups."))
        parser.add_option('-U', '--user', dest="user", metavar="LOGIN", help=_(
            "Login name of the user. This option must be specified when using "
            "a distinguished name as the value for USER."))
        parser.add_option('-m', '--mail', help=_("E-mail address of the user. "
            "The default is to use no e-mail address."))
        parser.add_option('-n', '--name', help=_("The name of the user. If the "
            "name contains a coma, the part before the coma will be used as "
            "the surname, the part after as the firstname."))
        parser.add_option('-o', '--non-unique', dest='unique',
            action='store_false', help=_("Allow the creation of a user account "
            "with a duplicate (non-unique) UID."))
        parser.add_option('-s', '--shell', help=_("The name of the user's "
            "login shell. The default is to use the shell as specified in the "
            "configuration file."))
        parser.add_option('-u', '--uid', help=_("The numerical value of the "
            "user's ID. This value must be unique, unless the -o option is "
            "used. The value must be non-negative. The default is to use the "
            "smallest ID value greater than UID_MIN and greater than every "
            "other user."))
        super(Useradd, self)._init_option_parser(parser)

    def _fix_settings(self, settings):
        super(Useradd, self)._fix_settings(settings)
        settings['UID_MIN'] = int(settings.get('UID_MIN') or 1000)
        settings['UID_MAX'] = int(settings.get('UID_MAX') or 60000)
        settings['SHELL'] = settings.get('SHELL') or '/bin/bash'
        settings['HOME'] = settings.get('HOME') or '/home/%(user)s'

    def _fix_params(self, args, kwargs):
        super(Useradd, self)._fix_params(args, kwargs)
        # If a distinguished name is used for the user, an explicit username
        # must be set otherwise we can implicitly determine it from the user.
        if len(args) != 1:
            raise ValueError(_("Wrong number of arguments"))
        if self.is_dn(args[0]) and not kwargs.get('user'):
            raise ValueError(_("Username must be supplied when using a "
                "distinguished name as the user argument."))
        kwargs['user'] = kwargs.get('user') or args[0]
        # If a group is specified, attempt to resolve it. If no group is
        # specified, _create_ldif will attempt to create one.
        kwargs['group'] = kwargs.get('group')
        if kwargs['group'] is not None:
            group = self.find_group(kwargs['group'])
            if not group:
                raise ValueError(_("The group '%s' does not exist") %
                    kwargs['group'])
            kwargs['group'] = group
        # Supplemental groups
        groups = []
        for id in list(kwargs.get('groups') or []):
            group = self.find_group(id)
            if not group:
                raise ValueError(_("The group '%s' does not exist") % id)
            groups.append(group)
        kwargs['groups'] = groups
        # If no uid is specified, _create_ldif will set one.
        if kwargs.get('uid') is not None:
            try:
                kwargs['uid'] = int(kwargs['uid'])
            except ValueError:
                raise ValueError(_("Invalid UID '%s'") % kwargs['uid'])
        else:
            kwargs['uid'] = None
        # Determine the common and surname of the user
        kwargs['name'] = kwargs.get('name') or kwargs['user']
        names = kwargs['name'].split(',', 1)
        kwargs['surname'] = names[0].strip()
        if len(names) > 1:
            kwargs['firstname'] = names[1].strip()
        else:
            kwargs['firstname'] = None
        # Remaining params
        kwargs['comment'] = kwargs.get('comment')
        kwargs['home'] = kwargs.get('home') or self.settings['HOME']
        kwargs['mail'] = kwargs.get('mail')
        kwargs['unique'] = kwargs.get('unique') != False
        kwargs['shell'] = kwargs.get('shell') or self.settings['SHELL']
        # Finally, construct the dn from the above params if necessary
        args[0] = self.get_user_dn(args[0], kwargs)

    def create_ldif(self, dn, **kwargs):
        records = RecordList()
        user = User(dn)
        # Ensure unique username
        if self.find_user(kwargs['user']):
            raise ValueError(_("User %s already exists") % kwargs['user'])
        user.uid = kwargs['user']
        # Ensure a valid UID
        if kwargs['uid'] is None:
            user.uidNumber = str(self.first_free_uid())
        else:
            if kwargs['unique'] and not self.is_free_uid(kwargs['uid']):
                raise ValueError(_("UID %s is not unique") % kwargs['uid'])
            user.uidNumber = str(kwargs['uid'])
        # Create a group for the user if no GID is specified
        if kwargs['group'] is None:
            group = self.create_group_ldif(kwargs)
            records.append(group)
            kwargs['group'] = group
        user.gidNumber = str(kwargs['group'].gidNumber[0])
        # Set remaining options
        user.commonName = kwargs['name']
        user.surname = kwargs['surname']
        user.givenName = kwargs['firstname']
        user.description = kwargs['comment']
        user.homeDirectory = self.format_string(kwargs['home'], kwargs)
        user.mail = kwargs['mail']
        user.loginShell = kwargs['shell']
        records.append(user)
        # Add user to any supplemental groups
        for group in kwargs['groups']:
            add_user = ModifyChangeRecord(group.dn)
            if self.settings['POSIX_GROUP_MODE']:
                add_user.add(self.settings['GROUP_MEMBER_FIELD'], user.uid)
            else:
                add_user.add(self.settings['GROUP_MEMBER_FIELD'], user.dn)
            records.append(add_user)
        return records

    def create_group_ldif(self, user_kwargs):
        groupadd = Groupadd(Settings(self.settings))
        groupadd.server = self.server
        args = [ user_kwargs['user'] ]
        kwargs = {
            'gid': user_kwargs['uid'],
            'unique': True,
        }
        groupadd._fix_params(args, kwargs)
        return groupadd.create_ldif(*args, **kwargs)[0]

    def first_free_uid(self):
        """Return the number of the first free UID or raise an exception if no
        more UIDs are available.

        """
        kwargs = {}
        kwargs['base'] = self.settings['LDAP_BASE']
        kwargs['scope'] = Server.SCOPE_SUBTREE
        kwargs['filter'] = "(objectClass=posixAccount)"
        kwargs['attr_list'] = ["uidNumber"]
        users = [
            int(x['uidNumber'][0]) for x in self.server.search(**kwargs)
            if self.settings['UID_MIN'] \
                <= int(x['uidNumber'][0]) \
                <= self.settings['UID_MAX']
        ]
        if not users:
            return self.settings['UID_MIN']
        uid = max(users) + 1
        if uid > self.settings['UID_MAX']:
            raise ValueError(_("No free UIDs available"))
        return uid

    def is_free_uid(self, uid):
        """Return True if the UID is still available."""
        return self.find_user(uid) is None


class Groupadd(AccountCommand):
    """Command to add a new group."""

    @classmethod
    def name(cls):
        return 'groupadd'

    def _init_option_parser(self, parser):
        parser.set_description(_("create a new group"))
        parser.add_argument('group')
        parser.add_option('-c', '--comment', help=_("Any text string. It can "
            "be used to specify a short description of the group."))
        parser.add_option('-g','--gid', help=_("The numerical value of the "
            "group's ID. This value must be unique unless the -o option is "
            "used. The value must be non-negative. The default is to use the "
            "first available available value between GID_MIN and GID_MAX as "
            "defined in the configuration file."))
        parser.add_option('-G', '--group', help=_("Name of the group. "
            "This option must be specified when using a distinguished name as "
            "the value for GROUP."))
        parser.add_option('-o', '--non-unique', dest='unique',
            action='store_false', help=_("Allow the creation of a group "
            "with a duplicate (non-unique) GID."))
        super(Groupadd, self)._init_option_parser(parser)

    def _fix_settings(self, settings):
        super(Groupadd, self)._fix_settings(settings)
        settings['GID_MIN'] = int(settings.get('GID_MIN') or 100)
        settings['GID_MAX'] = int(settings.get('GID_MAX') or 60000)
        if settings['GID_MIN'] > settings['GID_MAX']:
            raise ValueError(_("GID_MIN must be smaller than GID_MAX"))

    def _fix_params(self, args, kwargs):
        super(Groupadd, self)._fix_params(args, kwargs)
        # If a distinguished name is used for the group, an explicit groupname
        # must be set otherwise we can implicitly determine it from the group.
        if len(args) != 1:
            raise ValueError(_("Wrong number of arguments"))
        if self.is_dn(args[0]) and not kwargs.get('group'):
            raise ValueError(_("Group name must be supplied when using a "
                "distinguished name as the group argument."))
        kwargs['group'] = kwargs.get('group') or args[0]
        # If no gid is specified, _create_ldif will set one.
        if kwargs.get('gid') is not None:
            try:
                kwargs['gid'] = int(kwargs['gid'])
            except ValueError:
                raise ValueError(_("Invalid GID '%s'") % kwargs['gid'])
        else:
            kwargs['gid'] = None
        # Remaining params
        kwargs['comment'] = kwargs.get('comment')
        kwargs['unique'] = kwargs.get('unique') != False
        # Finally, construct the dn from the above params if necessary
        args[0] = self.get_group_dn(args[0], kwargs)

    def create_ldif(self, dn, **kwargs):
        group = Group(dn)
        # Ensure unique group name
        if self.find_group(kwargs['group']):
            raise ValueError(_("Group %s already exists") % kwargs['group'])
        group.cn = kwargs['group']
        # Ensure a valid GID
        if kwargs['gid'] is None:
            group.gidNumber = str(self.first_free_gid())
        else:
            if kwargs['unique'] and not self.is_free_gid(kwargs['gid']):
                raise ValueError(_("GID %s is not unique") % kwargs['gid'])
            group.gidNumber = str(kwargs['gid'])
        group.description = kwargs['comment']
        return RecordList([group])

    def first_free_gid(self):
        """Return the number of the first free GID or raise an exception if no
        more GIDs are available.

        """
        kwargs = {}
        kwargs['base'] = self.settings['LDAP_BASE']
        kwargs['scope'] = Server.SCOPE_SUBTREE
        kwargs['filter'] = "(objectClass=posixGroup)"
        kwargs['attr_list'] = ["gidNumber"]
        groups = [
            int(x['gidNumber'][0]) for x in self.server.search(**kwargs)
            if self.settings['GID_MIN'] \
                <= int(x['gidNumber'][0]) \
                <= self.settings['GID_MAX']
        ]
        if not groups:
            return self.settings['GID_MIN']
        gid = max(groups) + 1
        if gid > self.settings['GID_MAX']:
            raise ValueError(_("No free GIDs available"))
        return gid

    def is_free_gid(self, gid):
        """Return True if *gid* is still available."""
        return self.find_group(gid) is None


class Userdel(AccountCommand):
    """Command to delete a user."""

    @classmethod
    def name(cls):
        return 'userdel'

    def _init_option_parser(self, parser):
        parser.set_description(_("delete a user"))
        parser.add_argument('user')
        super(Userdel, self)._init_option_parser(parser)

    def _fix_params(self, args, kwargs):
        super(Userdel, self)._fix_params(args, kwargs)
        if len(args) != 1:
            raise ValueError(_("Wrong number of arguments"))
        user = self.find_user(args[0])
        if not user:
            raise ValueError(_("The user '%s' does not exist") % args[0])
        args[0] = user

    def create_ldif(self, user, **kwargs):
        changes = RecordList()
        changes.append(DeleteChangeRecord(user.dn))
        return changes


class Groupdel(AccountCommand):
    """Command to delete a group."""

    @classmethod
    def name(cls):
        return 'groupdel'

    def _init_option_parser(self, parser):
        parser.set_description(_("delete a group"))
        parser.add_argument('group')
        super(Groupdel, self)._init_option_parser(parser)

    def _fix_params(self, args, kwargs):
        super(Groupdel, self)._fix_params(args, kwargs)
        if len(args) != 1:
            raise ValueError(_("Wrong number of arguments"))
        group = self.find_group(args[0])
        if not group:
            raise ValueError(_("The group '%s' does not exist") % args[0])
        args[0] = group

    def create_ldif(self, group, **kwargs):
        changes = RecordList()
        changes.append(DeleteChangeRecord(group.dn))
        return changes


