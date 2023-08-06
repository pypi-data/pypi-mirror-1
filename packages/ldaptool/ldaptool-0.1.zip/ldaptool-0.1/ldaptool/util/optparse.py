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

"""Customized OptionParser for ldaptool."""

from __future__ import absolute_import

# We want to import everything from optparse into the current namespace but
# still want to be able to access the old OptionParser whose definition we
# override below.
from optparse import *
import optparse

from ldaptool.util.i18n import ugettext as _
from ldaptool.util.i18n import ungettext


def check_list(option, opt, value):
    return value.split(',')


class Option(optparse.Option):
    TYPES = optparse.Option.TYPES + ("list",)
    TYPE_CHECKER = dict(optparse.Option.TYPE_CHECKER)
    TYPE_CHECKER["list"] = check_list


class Argument(object):

    def __init__(self, *args, **kwargs):
        
        if len(args) != 1:
            raise ValueError(
                _("Argument constructor takes exactly 1 argument, %s given") %
                len(args)
            )
        self.name = args[0]
        self.required = ('required' not in kwargs) or kwargs['required']
        self.metavar = kwargs.get('metavar', self.name.replace('-','_').upper())


class OptionParser(optparse.OptionParser, object):
    """Custom OptionParser that knows about positional arguments."""

    def __init__(self, argument_class=Argument, **kwargs):
        kwargs['option_class'] = kwargs.get('option_class', Option)
        super(OptionParser, self).__init__(**kwargs)
        self.argument_class = argument_class
        self._create_argument_list()
        self._create_argument_mapping()

    def _create_argument_list(self):
        self.argument_list = []

    def _create_argument_mapping(self):
        self._args = {}

    def add_argument(self, *args, **kwargs):
        """Add an arguments to the parser.

            add_argument(Argument)
            add_argument(arg_str, ..., kwarg=val, ...)

        """
        if isinstance(args[0], basestring):
            argument = self.argument_class(*args, **kwargs)
        elif len(args) == 1 and not kwargs:
            argument = args[0]
        else:
            raise ValueError("invalid arguments")
        self._check_arg_conflict(argument)
        self.argument_list.append(argument)
        self._args[argument.name] = argument
        return argument

    def _check_arg_conflict(self, arg):
        if arg.name in self._args:
            raise ArgumentConflictError(
                _("Argument %s already exists") % arg.name
            )

    def set_usage(self, usage):
        if usage is None and hasattr(self, 'argument_list'):
            self.usage = ' '.join(["%prog [options]"] + \
                [ "%s" % x.metavar for x in self.required_arguments() ] + \
                [ "[%s]" % x.metavar for x in self.optional_arguments() ]
            )
        else:
            super(OptionParser, self).set_usage(usage)

    def required_arguments(self):
        return [ x for x in self.argument_list if x.required ]

    def optional_arguments(self):
        return [ x for x in self.argument_list if not x.required ]

    def check_values(self, values, args):
        req_arg_count = len(self.required_arguments())
        opt_arg_count = len(self.optional_arguments())
        if len(args) < req_arg_count:
            self.error(ungettext(
                "Command expects an argument",
                "Command expects %(num)d arguments",
                req_arg_count
            ))
        if len(args) > req_arg_count + opt_arg_count:
            self.error(ungettext(
                "Command expects no more than one argument",
                "Command expects no more than %(num)d arguments",
                req_arg_count + opt_arg_count
            ))

        return (values, args)

    def error(self, msg):
        """Raise error message."""
        err = OptParseError("%s\n%s" % (self.get_usage(), msg))
        err.exit_code = 2
        raise err


class AgnosticOptionParser(OptionParser):
    """OptionParser that does not care about bad options."""

    def _process_long_opt(self, rargs, values):

        try:
            return OptionParser._process_long_opt(self, rargs, values)
        except optparse.AmbiguousOptionError, err:
            raise err
        except BadOptionError:
            pass


    def _process_short_opts(self, rargs, values):

        try:
            return OptionParser._process_short_opts(self, rargs, values)
        except optparse.AmbiguousOptionError, err:
            raise err
        except BadOptionError:
            pass


    def check_values(self, values, args):
        return (values, args)


class ArgumentError(OptParseError):
    pass
ArgumentError.exit_code = 2

class ArgumentConflictError(ArgumentError):
    pass

