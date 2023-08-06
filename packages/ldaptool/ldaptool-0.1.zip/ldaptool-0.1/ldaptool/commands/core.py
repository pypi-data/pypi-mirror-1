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

import sys

from ldaptool.settings import Settings
from ldaptool.util import OptionParser
from ldaptool.util import SubclassResponsibility


"""Core command classes.

This module defines the core of the command classes, they are not in fact
specific to the ldaptool console command.

"""

__all__ = ('Command', 'ConsoleCommand')


class Command(object):
    """A command encapsulates a particular command such as creating a directory
    or deleting a file."""

    def __init__(self, settings=None):
        """Initialize the command.

        If settings is supplied, the settings the command wil use are
        initialized using the :meth:`set_settings` method.

        """
        if settings is not None:
            self.set_settings(settings)

    def call(self, *args, **kwargs):
        """Call this command.

        The command will be called using *args* and *kwargs* as the positional
        arguments and options. This will first call :meth:`_fix_params` so that
        we have a change to add required parameters and check the existing
        parameters for validity.

        Subclasses should *not* override this method but rather override
        :meth:`_execute` instead.

        """
        args = list(args)
        self._fix_params(args, kwargs)
        return self._execute(*args, **kwargs)

    def set_settings(self, settings):
        """Set the settings to *settings*.

        This will call :meth:`_fix_settings` so that the instance has a change
        to add required settings and check existing settings for validity. Note
        that *settings* will be modified so you might want to create a copy as
        follows: ``cmd.set_settings(Settings(settings))``.

        """
        self._settings = settings
        self._fix_settings(self._settings)

    def get_settings(self):
        """Return the settings that this command should use.

        If the settings had not been previously set, a new :class:`Settings`
        object will be created and passed by :meth:`fix_settings` to ensure that
        we at least have some default values to work with.

        """
        if not hasattr(self, '_settings') or self._settings is None:
            self.set_settings(Settings())
        return self._settings

    settings = property(get_settings, set_settings)

    def _execute(self, *args, **kwargs):
        """Execute this command.

        Subclasses should override this to do something sensible.

        Client should not call this method directly. Instead, the should call
        :meth:`call` which will first run the argument by :meth:`_fix_params` so
        that the arguments can be verified for validity.

        """
        return 0

    def _fix_settings(self, settings):
        """Fix the *settings*.

        Subclasses should override this to set default values or to parse any
        simplified values in the configuration file. For example, the
        :conf:`COMMANDS` setting accepts a list of string which are converted
        into a list of :class:`Command` classes by :class:`Main`.

        """
        pass

    def _fix_params(self, args, kwargs):
        """Fix *args* and *kwargs* before running :meth:`_execute`.

        Subclasses should override this to set default values for missing
        arguments or to check the arguments for validity.

        """
        pass


class ConsoleCommand(Command):
    """A command that is intented to be used from the command-line as a
    sub-command of :ref:`ldaptool <usage>`.

    """

    @classmethod
    def name(self):
        """Return the name of the command.

        This is for example, used to determine the name of the sub-command on
        the command-line.

        """
        raise SubclassResponsibility()

    def dispatch(self, args=None):
        """Dispatch the command.

        Dispatch the command parsing the arguments in *args* first. If *args*
        is not defined, ``sys.args[1:]`` will be used instead.

        """
        if args is None:
            args = sys.args[1:]
        values, args = self.parse_args(args)
        return self.call(*args, **values.__dict__)

    def option_parser(self):
        """Return an :class:`OptionParser` to parse command line arguments into
        options.
        
        If the option parser had not been previously initialized, it will be
        before it is returned to the caller.

        """
        if not hasattr(self, '_parser') or self._settings is None:
            self._parser = self._option_parser_class()()
            self._init_option_parser(self._parser)
        return self._parser

    def _option_parser_class(self):
        """Return the class of the option parser that this console command
        should use.

        By default this will be :class:`OptionParser` but subclasses may choose
        to override this method to return a different implementation.

        """
        return OptionParser

    def _init_option_parser(self, parser):
        """Initialize the option parser.

        Subclasses should override this to add additional options. 

        """
        parser.set_usage(" ".join(["%%prog %s [options]" % self.name()] + \
            [ x.metavar for x in self._parser.required_arguments() ] + \
            [ "[%s]" % x.metavar for x in self._parser.optional_arguments() ])
        )

    def parse_args(self, args=None):
        """Parse the command line arguments.

        Returns a tuple as returned by :meth:`OptionParser.parse_args`. If
        *args* is not defined, ``sys.args[1:]`` will be used instead.
        
        """
        return self.option_parser().parse_args(args)

    def help(self):
        """Print the help for this command on stdout."""
        return self.option_parser().format_help()

