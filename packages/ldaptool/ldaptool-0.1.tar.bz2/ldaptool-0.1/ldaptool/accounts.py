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

"""Additional classes to use and manipulate accounts and groups."""


import pwd
import grp

from ldaptool.ldap import Entry
from ldaptool.util.i18n import ugettext as _


__all__ = ('user_info', 'group_info', 'User', 'Group')


def user_info(uid):
    """Return a struct_passwd with user information for the uid or user name.

    The struct_passwd behave similar to a tuple. See python's documentation of
    pwd.struct_passwd for more information.

    Raises KeyError if if the user could not be found.
    """
    try:
        return pwd.getpwuid(int(uid))
    except (TypeError, ValueError), e:
        pass
    try:
        return pwd.getpwnam(uid)
    except KeyError:
        raise KeyError(_("User '%s' not found")%uid)



def group_info(gid):
    """Return a struct_group with group information for the gid or group name.

    The struct_group behave similar to a tuple. See python's documentation of
    grp.struct_group for more information.

    Raises KeyError if if the group could not be found.
    """
    try:
        return grp.getgrgid(int(gid))
    except (TypeError, ValueError), e:
        pass
    try:
        return grp.getgrnam(gid)
    except KeyError:
        raise KeyError(_("Group '%s' not found")%gid)


class User(Entry):

    def __init__(self, dn, attrs=None):
        super(User, self).__init__(dn, attrs)
        self['objectClass'] = [
            'posixAccount',
            'shadowAccount',
            'inetOrgPerson',
            'top'
        ]


class Group(Entry):

    def __init__(self, dn, attrs=None):
        super(Group, self).__init__(dn, attrs)
        self['objectClass'] = [ 'posixGroup', 'top' ]

