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


"""Settings for ldaptool."""

import os
import imp
from tempfile import mkstemp


__all__ = ('Settings','ConfigurationError')


class Settings(dict, object):

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            if isinstance(args[0], basestring) or isinstance(args[0], file):
                self.load(args[0])
                return
        super(Settings, self).__init__(*args, **kwargs)

    def load(self, f):
        if isinstance(f, basestring):
            f = file(f, 'r')
            try:
                self.load(f)
            finally:
                f.close()
            return
        try:
            handle = None
            if not hasattr(f, 'name'):
                handle, file_name = mkstemp('.py')
            else:
                file_name = f.name
            m = imp.load_source('settings', file_name, f)
            if handle is not None:
                os.remove(file_name)
            os.remove(file_name + 'c')
            for key, value in m.__dict__.iteritems():
                if key[:1] == '_':
                    continue
                self[key] = value
        except Exception, err:
            raise ConfigurationError(err)

    def __repr__(self):
        return "Settings(%s)" % super(Settings, self).__repr__()

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError("No attribute %r" % key)

    def __add__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        d = Settings()
        d.update(self)
        d.update(other)
        return d

    def __radd__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        d = Settings()
        d.update(other)
        d.update(self)
        return d

    def __iadd__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        self.update(other)
        return self


class ConfigurationError(Exception):
    pass

