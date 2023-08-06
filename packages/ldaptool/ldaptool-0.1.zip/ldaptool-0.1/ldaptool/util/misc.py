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

"""Miscellaneous utilities that did not fit anywhere else."""

from itertools import chain


def is_iterable(obj):
    """Return ``True`` if *obj* is iterable."""
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def is_url(url):
    return hasattr(url, 'geturl')

def is_string(obj):
    return isinstance(obj, basestring)

def is_intlike(obj):
    try:
        int(obj)
        return True
    except ValueError:
        return False

class SubclassResponsibility(NotImplementedError):
    
    def __init__(self, *args):
        if not args:
            args = ['A subclass should have overridden this method.']
        NotImplementedError.__init__(self, *args)


class KeyMappedDict(dict):

    def __init__(self, *args, **kwargs):
        # Can't set passed dictionary items via super, as super constructor does
        # not use __setitem__ (see below)
        super(KeyMappedDict, self).__init__()
        # Allow unknown keys
        if 'allow_unknown_keys' in kwargs:
            self.allow_unknown_keys = kwargs['allow_unknown_keys']
            del kwargs['allow_unknown_keys']
        else:
            self.allow_unknown_keys = False
        # Case sensitivity
        if 'case_sensitive' in kwargs:
            self.case_sensitive = kwargs['case_sensitive']
            del kwargs['case_sensitive']
        else:
            self.case_sensitive = True
        # Process permissable keys
        self.key_map = {}
        if 'key_map' in kwargs:
            for key,aliases in (kwargs['key_map'] or []):
                self.add_key(key, aliases)
            del kwargs['key_map']
        # Set the dictionary items
        for arg in args:
            if hasattr(arg, 'iteritems'):
                arg = arg.iteritems()
            for key,value in arg:
                self[key] = value
        for key,value in kwargs.iteritems():
            self[key] = value

    def add_key(self, key, aliases=None):
        """Add a key to the list of permissable keys."""
        if is_string(aliases):
            aliases = [ aliases ]
        aliases = aliases or []
        for x in chain([key], aliases):
            if not self.case_sensitive:
                x = x.lower()
            if x in self.key_map:
                raise KeyError("Key already exists: %s" % x)
        for x in chain([key], aliases):
            if not self.case_sensitive:
                x = x.lower()
            self.key_map[x] = key

    def remove_key(self, key):
        """Remove a key and all aliases pointing to it."""
        if not self.case_sensitive:
            key = key.lower()
        nothing_deleted = True
        for x,value in self.key_map.items():
            if not self.case_sensitive:
                value = value.lower()
            if value == key:
                del self.key_map[x]
                nothing_deleted = False
        if nothing_deleted:
            raise KeyError(key)

    def remove_alias(self, alias):
        """Remove a key alias."""
        if not self.case_sensitive:
            alias = alias.lower()
            value = self.key_map[alias].lower()
        else:
            value = self.key_map[alias]
        if value == alias:
            raise KeyError("Item is a key and not an alias: %s" % alias)
        del self.key_map[alias]

    def __setitem__(self, key, value):
        super(KeyMappedDict, self).__setitem__(self._normalize_key(key), value)

    def __getitem__(self, key):
        return super(KeyMappedDict, self).__getitem__(self._normalize_key(key))

    def __delitem__(self, key):
        return super(KeyMappedDict, self).__delitem__(self._normalize_key(key))

    def _normalize_key(self, key):
        """Return the normalized key for *key* by following the known aliases.

        Will raise a KeyError if the key is not in the key map and
        ``allow_unknown_keys`` is false.
        
        """
        try:
            if self.case_sensitive:
                return self.key_map[key]
            else:
                return self.key_map[key.lower()]
        except KeyError:
            if self.allow_unknown_keys:
                return key
            raise KeyError("Illegal key: %s" % key)

    def __repr__(self):
        key_map = dict()
        for key,value in self.key_map.iteritems():
            if value not in key_map:
                key_map[value] = []
            if key != value:
                key_map[value].append(key)
        return "KeyMappedDict(%s, allow_unknown_keys=%r, case_sensitive=%r, " \
            "key_map=%r)" % (
            super(KeyMappedDict, self).__repr__(),
            self.allow_unknown_keys,
            self.case_sensitive,
            key_map.items()
        )

