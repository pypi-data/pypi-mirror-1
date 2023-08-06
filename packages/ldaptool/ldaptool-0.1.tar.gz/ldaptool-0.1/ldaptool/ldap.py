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


"""Classes for creating and manipulating LDAP objects.

The ldap module allows clients to interact with the server in an object-oriented
way without having to worry about implementation specific details.

The :class:`Record` and :class:`RecordList` objects represent themselves in an
LDIF compatible way when printed, which makes it easy to export that to an LDIF
file.

.. seealso::
    :rfc:`2849` - The LDAP Data Interchange Format (LDIF)

"""


from __future__ import absolute_import

from base64 import b64encode
from itertools import repeat,izip,chain
import ldap as pythonldap

from ldaptool.util import SubclassResponsibility, KeyMappedDict, is_iterable, \
    is_url


__all__ = (
    'SAFE_CHARS', 'SAFE_INIT_CHARS', 'is_safe_string', 'get_safe_string',
    'Server', 'SynchronousServer', 'AsynchronousServer', 'RecordList',
    'AttrValContainer', 'Record', 'Entry', 'ChangeRecord', 'AddChangeRecord',
    'DeleteChangeRecord', 'RenameChangeRecord', 'ModifyChangeRecord',
    'Modification', 'AddModification', 'DeleteModification',
    'ReplaceModification'
)


SAFE_CHARS = "\x01\x02\x03\x04\x05\x06\x07\x08\t\x0b\x0c\x0e\x0f\x10\x11\x12"  \
    "\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !\"#$%&'()*+,-./012" \
    "3456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxy" \
    "z{|}~\x7f"
SAFE_INIT_CHARS = "\x01\x02\x03\x04\x05\x06\x07\x08\t\x0b\x0c\x0e\x0f\x10\x11" \
    "\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f!\"#$%&'()*+,-./" \
    "0123456789;=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwx" \
    "yz{|}~\x7f"


def is_safe_string(string):
    """Return True if this string is LDIF safe.

    """
    if not isinstance(string, basestring):
        string = unicode(string)
    if len(string) == 0:
        return True
    if string[0] not in SAFE_INIT_CHARS:
        return False
    for char in string[1:]:
        if char not in SAFE_CHARS:
            return False
    return True


def get_safe_string(obj):
    """Return a string representation of the object that has been base64 encoded
    if necessary.

    """
    if isinstance(obj, unicode):
        obj = obj.encode('UTF-8')
    if not isinstance(obj, basestring):
        obj = unicode(obj)
    if is_safe_string(obj):
        return obj
    return b64encode(obj)


class Server(object):
    """Abstract superclass for LDAP server implementations.

    This allows us to create a convenient interface around python-ldap's
    LDAPObject interface for synchronous (:class:`SynchronousServer`) and
    asynchronous connections (:class:`AsynchronousServer`).

    """

    MOD_ADD = pythonldap.MOD_ADD
    MOD_DELETE = pythonldap.MOD_DELETE
    MOD_REPLACE = pythonldap.MOD_REPLACE
    SCOPE_BASE = pythonldap.SCOPE_BASE
    SCOPE_ONELEVEL = pythonldap.SCOPE_ONELEVEL
    SCOPE_SUBTREE = pythonldap.SCOPE_SUBTREE

    def search(self, base, scope=SCOPE_SUBTREE,
            filter='(objectClass=*)', attr_list=None, desc_only=False,
            timeout=-1, size_limit=0):
        raise NotImplementedError()

    def add(self, dn, modlist):
        raise NotImplementedError()

    def delete(self, dn):
        raise NotImplementedError()

    def modify(self, dn, modlist):
        raise NotImplementedError()

    def rename(self, dn, newrdn, newsuperior=None, delete=True):
        raise NotImplementedError()

    def passwd(self, dn, oldpw=None, newpw=None):
        raise NotImplementedError()


class SynchronousServer(Server):
    """A wrapper around python-ldap's LDAPObject that users synchronous
    communication with the server.

    """

    def __init__(self, uri):
        self._server = pythonldap.initialize(uri)

    def bind(self, binddn, password):
        self._server.simple_bind_s(binddn, password)

    def search(self, base, scope=Server.SCOPE_SUBTREE,
            filter='(objectClass=*)', attr_list=None, desc_only=False,
            timeout=-1, size_limit=0):
        return RecordList(Entry(x[0], x[1]) for x in self._server.search_ext_s(
            base, scope, filter, attr_list, desc_only, None, None, timeout,
            size_limit
        ))

    def add(self, dn, modlist):
        self._server.add_s(dn, modlist)

    def delete(self, dn):
        self._server.delete_s(dn)

    def modify(self, dn, modlist):
        self._server.modify_s(dn, modlist)

    def rename(self, dn, newrdn, newsuperior=None, delete=True):
        self._server.rename_s(dn, newrdn, newsuperior, delete)

    def passwd(self, dn, oldpw=None, newpw=None):
        self._server.passwd_s(dn, oldpw, newpw)


class AsynchronousServer(Server):
    """A wrapper around python-ldap's LDAPObject that users asynchronous
    communication with the server.

    .. note::

        This class is currently note implemented.

    """

    pass


class RecordList(list):
    """A list of :class:`Record` objects."""    

    def apply_to_server(self, server):
        """Apply all Records to *server* by calling
        :meth:`Record.apply_to_server` on each of them.

        Please note that the records are not added atomicly. If any fail, you
        will need to role-back manually.

        """
        for each in self:
            each.apply_to_server(server)

    def __repr__(self):
        return 'RecordList(%s)' % repr(list(self))[1:-1]

    def __str__(self):
        ret = u"version: 1\n\n"
        for record in self:
            ret += u"%s\n" % str(record.as_change_record())
        return ret


class AttrValContainer(object):
    """Abstract superclass for classes that consist of attribute/value pairs.

    Subclasses must implement :meth:`_attrvals` which returns a list of the
    attribute/value pairs. For example::

        (
            ('dn': "dc=example,dc=org"),
            ('dc': "example"),
            ('objectClass': "dcObject"),
        )

    This class is used by the LDAP :class:`Record` and related types.

    """

    def _attrvals(self):
        """Return a list of attribute/value tuples for this object."""
        return ()

    def __str__(self):
        res = ""
        for attrval in self._attrvals():
            if isinstance(attrval, AttrValContainer):
                res += "%s-\n" % attrval
            elif is_url(attrval[1]):
                res += "%s:< %s\n" % (
                    attrval[0],
                    get_safe_string(attrval[1].geturl())
                )
            elif is_safe_string(attrval[1]):
                res += "%s: %s\n" % (
                    attrval[0],
                    attrval[1]
                )
            else:
                res += "%s:: %s\n" % (
                    attrval[0],
                    get_safe_string(attrval[1])
                )
        return res


class Record(AttrValContainer):
    """An LDAP Record.

    This can either be an :class:`Entry` or a :class:`ChangeRecord`.
    Essentially, this corresponds to records in an LDIF file.

    Records know how to apply themselves to a server by overriding the
    :meth:`apply_to_server` method.

    """

    def __init__(self, dn):
        self.dn = dn

    def _attrvals(self):
        return (('dn', self.dn),)

    def as_change_record(self):
        """Return a :class:`ChangeRecord` for this record.
        
        Subclasses of :class:`ChangeRecord` will probably will just want to
        return themselves while :class:`Entry` classes will want to return an
        :meth:`AddChangeRecord`.
        
        """
        raise NotImplementedError()

    def apply_to_server(self, server):
        """Apply this Record to the server as a change record."""
        raise NotImplementedError()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.dn)


class Entry(Record):
    """An Entry Record."""

    def __init__(self, dn, attrs=None):
        super(Entry, self).__init__(dn)
        self.attrs = {}
        if attrs:
            for key,value in attrs.iteritems():
                self[key] = value

    def as_change_record(self):
        return AddChangeRecord(self)

    def apply_to_server(self, server):
        return self.as_change_record().apply_to_server(server)

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        if hasattr(self, name) or name in ['attrs', 'dn']:
            super(Entry, self).__setattr__(name, value)
            return
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __getitem__(self, key):
        key = self._normalize_key(key)
        if key == 'dn':
            return self.dn
        return self.attrs[key]

    def __setitem__(self, key, value):
        if key == 'dn':
            self.dn = self._normalize(key, value)[1]
            return
        key, value = self._normalize(key, value)
        if len(value) == 0:
            try:
                del self[key]
            except KeyError:
                pass
            return
        self.attrs[key] = value

    def __delitem__(self, key):
        key = self._normalize_key(key)
        if key == 'dn':
            raise KeyError("Attribute 'dn' can not be removed.")
        del self.attrs[key]

    def _normalize(self, key, value):
        key = self._normalize_key(key)
        if value is None:
            value = []
        elif not isinstance(value, list):
            value = [ value ]
        return key, value

    def _normalize_key(self, key):
        return key

    def _attrvals(self):
        return tuple(self.iteritems())

    def iteritems(self):
        yield ('dn', self.dn)
        for key,values in self.attrs.iteritems():
            for value in values:
                yield (key, value)

    def itervalues(self):
        yield self.dn
        for values in self.attrs.itervalues():
            for value in values:
                yield value

    def iterkeys(self):
        yield 'dn'
        for key in self.attrs.iterkeys():
            yield key

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        return len(list(self.itervalues()))

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.dn, self.attrs)


class ChangeRecord(Record):
    """Abstract superclass for records that represent changes to the tree.

    Subclasses must implement :meth:`change_type` to return the type of change
    that they represent.

    """

    def change_type(self):
        """The type of change that this class represents."""
        raise NotImplementedError()

    def as_change_record(self):
        return self

    def _attrvals(self):
        return super(ChangeRecord, self)._attrvals() + (
            ('changetype', self.change_type()),
        )


class AddChangeRecord(ChangeRecord):
    """Change record that adds a new entry to the tree."""

    def __init__(self, entry):
        self.entry = entry

    @property
    def dn(self):
        return self.entry.dn

    def change_type(self):
        return 'add'

    def apply_to_server(self, server):
        modlist = [ (x[0],[str(y) for y in x[1]]) for x in self.entry.attrs.iteritems() ]
        server.add(self.dn, modlist)

    def _attrvals(self):
        return super(AddChangeRecord, self)._attrvals() + \
            self.entry._attrvals()[1:]

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.entry)


class DeleteChangeRecord(ChangeRecord):
    """Change record that deletes a change record from the tree."""

    def apply_to_server(self, server):
        server.delete(self.dn)

    def change_type(self):
        return 'delete'


class RenameChangeRecord(ChangeRecord):
    """Change record that renames or copies an entry."""

    def __init__(self, dn, newrdn, delete=True, newsuperior=None):
        super(RenameChangeRecord,self).__init__(dn)
        self.newrdn = newrdn
        self.delete = delete
        self.newsuperior = newsuperior

    def apply_to_server(self, server):
        server.rename(self.dn, self.newrdn, self.newsuperior, self.delete)

    def change_type(self):
        return 'modrdn'

    def _attrvals(self):
        res = super(RenameChangeRecord, self)._attrvals() + (
            ('newrdn', self.newrdn),
            ('deleteoldrdn', int(self.delete)),
        )
        if self.newsuperior:
            res += (('newsuperior', self.newsuperior),)
        return res

    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.dn,
            self.newrdn,
            self.delete,
            self.newsuperior
        )


class ModifyChangeRecord(ChangeRecord):
    """Change record that performs a set of modifications to an entry."""
    
    def __init__(self, dn, modifications=None):
        super(ModifyChangeRecord, self).__init__(dn)
        if modifications is None:
            modifications = []
        self.modifications = modifications

    def apply_to_server(self, server):
        server.modify(self.dn, self._modlist())

    def add(self, attribute, values):
        """Add a modification that adds the specified values to the attribute.

        This is just a convenience for::

            record.modifications.append(AddModification(attribute, values))

        """
        self.modifications.append(AddModification(attribute, values))

    def delete(self, attribute, values=None):
        """Add a modification that deletes the specified attribute or just
        specific values from it.

        This is just a convenience for::

            record.modifications.append(DeleteModification(attribute, values))

        """
        self.modifications.append(DeleteModification(attribute, values))

    def replace(self, attribute, values=None):
        """Add a modification that replaces the specified attribute with a new
        list of values.

        This is just a convenience for::

            record.modifications.append(ReplaceModification(attribute, values))

        """
        self.modifications.append(ReplaceModification(attribute, values))

    def change_type(self):
        return 'modify'

    def _attrvals(self):
        return super(ModifyChangeRecord, self)._attrvals() + tuple(
            self.modifications
        )

    def _modlist(self):
        return [ x._modtuple() for x in self.modifications ]

    def __repr__(self):
        return "%s(%r, %r)" % (
            self.__class__.__name__,
            self.dn,
            self.modifications
        )

 
class Modification(AttrValContainer):
    """Modification specification used by :class:`ModifyChangeRecord`.

    Subclasses must override :meth:`modification_type` and
    :meth:`modification_operation`.

    """

    def __init__(self, attr, values=None):
        self.attr = attr
        self._values = []
        if values:
            self.values = values

    def set_values(self, values):
        if not isinstance(values, basestring) and not is_url(values) \
                and is_iterable(values):
            self._values = list(values)
        else:
            self._values.append(values)

    def get_values(self):
        return self._values

    values = property(get_values, set_values)

    def modification_type(self):
        """Returns the attribute that this mod-spec changes."""
        raise NotImplementedError()

    def modification_operation(self):
        """Returns an integer representing the type of modification."""
        raise NotImplementedError()

    def _attrvals(self):
        return ((self.modification_type(), self.attr),) + tuple(izip(
            repeat(self.attr), self.values
        ))

    def _modtuple(self):
        """Returns a tuple representing the modification."""
        return (self.modification_operation(), self.attr, self.values)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.attr, self.values)


class AddModification(Modification):
    """Modification specification that adds a value to an attribute."""

    def modification_operation(self):
        return Server.MOD_ADD

    def modification_type(self):
        return 'add'


class DeleteModification(Modification):
    """Modification specification that completely removes individual values from
    an attribute or completely removes an attribute.
    
    """

    def modification_operation(self):
        return Server.MOD_DELETE

    def modification_type(self):
        return 'delete'


class ReplaceModification(Modification):
    """Modification specification that replcaes an attribute with a new list of
    values.

    """

    def modification_operation(self):
        return Server.MOD_REPLACE

    def modification_type(self):
        return 'replace'


