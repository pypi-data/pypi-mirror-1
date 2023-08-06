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

"""Console commands for ldaptool."""


import sys
from os import environ
from os.path import basename

from ldaptool.commands.core import ConsoleCommand
from ldaptool.util import AgnosticOptionParser, SUPPRESS_HELP
from ldaptool.util import ugettext as _
from ldaptool.util import SubclassResponsibility
from ldaptool.util.optparse import ArgumentError
from ldaptool.util.messaging import Messenger
from ldaptool.settings import Settings, ConfigurationError
from ldaptool.ldap import SynchronousServer


__all__ = (
    'LdaptoolCommand', 'Main', 'Help', 'Version', 'LdapCommandClass',
    'LdapCommand'
)


# Locations of the default configuration files
DEFAULT_CONFIGS=('~/.ldaptool', '/etc/ldaptool')


class LdaptoolCommand(ConsoleCommand):
    """Superclass for commands in use by ldaptool.
    
    This adds some common behavior in use by all subclasses."""

    def _init_option_parser(self, parser):
        super(LdaptoolCommand, self)._init_option_parser(parser)
        parser.remove_option('-h')
        group = parser.add_option_group(_("Global options"))
        group.add_option('-h','--help', action="store_true", help=SUPPRESS_HELP)
        group.add_option('-f', '--config', help=_("Use the specified file as "
            "the configuration file."))
        group.add_option('-N', '--no-hooks', dest="run_hooks",
            action="store_false", help=_("Do not run any hooks."))
        group.add_option('--debug', action='store_true', help=_(
            "Enable debugging information"
        ))

    def _fix_params(self, args, kwargs):
        # Load the settings from a file if none has yet been set.
        if not hasattr(self, '_settings') or self._settings is None:
            if kwargs.get('config') is not None:
                self.set_settings(Settings(kwargs['config']))
            else:
                self._load_default_config()
        kwargs['help'] = kwargs.get('help') is True
        kwargs['run_hooks'] = kwargs.get('run_hooks') is not False
        kwargs['debug'] = kwargs.get('debug') is True

    def _load_default_config(self):
        f = None
        for config in DEFAULT_CONFIGS:
            if config[:1] == '~' and 'HOME' in environ:
                config = environ['HOME'] + config[1:]
            try:
                f = file(config, 'r')
                break
            except IOError:
                pass
        if f is None:
            # FIXME log something
            return
        self.set_settings(Settings(f))
        f.close()


class Main(LdaptoolCommand):
    """Base command for ldaptool.

    The only job of this config is to read the configuration file and then to
    delegate to one of the subcommands available.
    """

    @classmethod
    def name(cls):
        return None

    def _execute(self, *args, **kwargs):
        # Okay, try to figure out what to do
        if kwargs['help']:
            return Help(self.settings).dispatch(sys.argv[1:])
        if not args:
            return (2, None, Help(self.settings).dispatch(sys.argv[1:])[1])
        # Do we have a complete match somewhere?
        for name in args:
            command = self.settings['COMMANDS'].get(name)
            if command is not None:
                client_args = sys.argv[1:]
                client_args.remove(name)
                return command(self.settings).dispatch(client_args)
        raise ArgumentError(_("Unknown command %r") % name)

    def _fix_settings(self, settings):
        super(Main, self)._fix_settings(settings)
        commands = settings.get('COMMANDS')
        if commands is None:
            commands = self.default_commands()
        settings['COMMANDS'] = {}
        for name in commands:
            command = self._load_command(name)
            settings['COMMANDS'][command.name()] = command
        settings['HOOKS'] = settings.get('HOOKS', [])

    def default_commands(self):
        """
        Return the default commands that ldaptool will use if none are defined.
        
        """
        return [
            'ldaptool.commands.Help',
            'ldaptool.commands.Version',
            'ldaptool.commands.Useradd',
            'ldaptool.commands.Groupadd',
            'ldaptool.commands.Userdel',
            'ldaptool.commands.Groupdel',
        ]

    def _load_command(self, name):
        if not isinstance(name, basestring):
            return name
        try:
            module, cls = name.rsplit('.', 1)
            return getattr(__import__(module, fromlist=[''], level=0), cls)
        except (ImportError, AttributeError):
            exc_class, exc, tb = sys.exc_info()
            new_exc=ConfigurationError(_("Could not load command %s: %s") % (
                name, exc
            ))
            raise new_exc.__class__, new_exc, tb

    def _option_parser_class(self):
        return AgnosticOptionParser


class Help(LdaptoolCommand):
    """Command that displays help information for ldaptool."""

    @classmethod
    def name(cls):
        return 'help'

    def _init_option_parser(self, parser):
        parser.set_description(_("show help for a command"))
        parser.add_argument('command', required=False)
        super(Help, self)._init_option_parser(parser)

    def _execute(self, command=None, **kwargs):
        if not command:
            return (0, self.general_usage(), None)
        if not command in self.settings['COMMANDS']:
            raise ArgumentError(_("Unknown command %r") % command)
        return (0, self.settings['COMMANDS'][command]().help(), None)

    def general_usage(self):
        """Return a string with the general usage description of ldaptool."""
        import ldaptool.version
        return _("""usage: %(prog)s <command> [options] [arguments]
ldaptool command-line client, version %(version)s

type '%(prog)s help <command>' for help on a specific command.

Available subcommands:
%(subcommands)s

ldaptool is a tool for manipulating LDAP databases.""") % {
            'prog': basename(sys.argv[0]),
            'version': ldaptool.version.release_string(),
            'subcommands': "\n".join([
                "   %s" % x for x in self.settings['COMMANDS'].keys() ]),
        }


class Version(LdaptoolCommand):
    """A command that shows version information on ldaptool."""

    @classmethod
    def name(cls):
        return 'version'

    def _init_option_parser(self, parser):
        parser.set_description(_("show version information"))
        super(Version, self)._init_option_parser(parser)

    def _execute(self, **kwargs):
        import ldaptool.version
        return (0, _(
            "%(prog)s command-line client, version %(release)s\n\n"
            "Copyright (c) 2008 University of Bern.\n"
            "Licensed under the terms of the GNU Public License (GPL).\n"
            ) % {
            'prog': basename(sys.argv[0]),
            'release': ldaptool.version.release_string()
        }, None)


class LdapCommandClass(type):

    @property
    def PRE_COMMIT(cls):
        """Pre-commit event."""
        return '%s.pre' % cls.name()

    @property
    def POST_COMMIT(cls):
        """Post-commit event."""
        return '%s.post' % cls.name()


class LdapCommand(LdaptoolCommand):
    """Abstract superclass for LDAP based command.

    This simplifies the creation of commands that manipulate the LDAP tree.
    LDAP based commands need only return an LDIF of the changes they would like
    to propogate.
    """

    __metaclass__ = LdapCommandClass

    def __init__(self, settings=None):
        super(LdapCommand, self).__init__(settings)
        self.server = None

    def _init_option_parser(self, parser):
        group = parser.add_option_group(_("LDAP options"))
        group.add_option('-D', '--binddn', help=_("Use the Distinguished Name "
            "BINDDN to bind to the LDAP directory. The default is to use the "
            "value of BIND_DN in the configuration file."))
        group.add_option('-H', '--ldapuri', type='list', help=_(
            "URIs of the ldap servers to use. Each URI is separated from the "
            "next by a coma with no intervening whitespace. The default is to "
            "use the value of LDAP_URI in the configuration file."))
        group.add_option('-w', '--passwd', help=_("Use PASSWD as the password "
            "for authentication. The default is to use LDAP_PASSWD in the "
            "configuration file if it is defined."))
        group.add_option('-y', '--passwd-file', help=_("Use complete contents "
            "of PASSWD_FILE as the password for authentication. The default is "
            "to use LDAP_PASSWD_FILE in the configuration file if it is "
            "defined."))
        group.add_option('-p','--pretend', dest="pretend", action='store_true',
            help=_("Do not actually write any data. This will print the changes"
            " that would be made and exit."))
        super(LdapCommand, self)._init_option_parser(parser)

    def _fix_settings(self, settings):
        super(LdapCommand, self)._fix_settings(settings)
        settings['LDAP_URI'] = settings.get('LDAP_URI') or ['ldap://localhost']
        if not isinstance(settings['LDAP_URI'], list):
            settings['LDAP_URI'] = [ settings['LDAP_URI'] ]
        settings['LDAP_BASE'] = settings.get('LDAP_BASE') or "dc=example,dc=org"
        settings['BIND_DN'] = settings.get('BIND_DN') or None
        settings['BIND_PASSWD'] = settings.get('BIND_PASSWD') or None
        settings['BIND_PASSWD_FILE'] = settings.get('BIND_PASSWD_FILE') or None

    def _fix_params(self, args, kwargs):
        super(LdapCommand, self)._fix_params(args, kwargs)
        kwargs['pretend'] = kwargs.get('pretend') == True
        kwargs['ldapuri'] = kwargs.get('ldapuri') or self.settings['LDAP_URI']
        if kwargs.get('passwd') is None:
            kwargs['passwd'] = self.settings['BIND_PASSWD']
        if kwargs.get('passwd_file') is None:
            kwargs['passwd_file'] = self.settings['BIND_PASSWD_FILE']
        if kwargs['passwd_file'] is not None and kwargs['passwd'] is None:
            try:
                f = file(kwargs['passwd_file'], 'r')
                kwargs['passwd'] = f.read()
            finally:
                f.close()
        kwargs['binddn'] = kwargs.get('binddn') or self.settings['BIND_DN']
        if self.server is None:
            self._create_server(
                kwargs['ldapuri'],
                kwargs['binddn'],
                kwargs['passwd']
            )

    def create_ldif(self, *args, **kwargs):
        """Return an LDIF for the passed arguments that can be committed."""
        raise SubclassResponsibility()

    def _execute(self, *args, **kwargs):
        ldif = self.create_ldif(*args, **kwargs)
        self._pre_commit(ldif)
        if kwargs['pretend']:
            return ldif
        ldif.apply_to_server(self.server)
        self._post_commit(ldif)

    def _pre_commit(self, ldif):
        """Hook that is called before commit of ldif."""
        Messenger.default().notify(self.__class__.PRE_COMMIT, ldif)

    def _post_commit(self, ldif):
        """Hook that is called after commit of ldif."""
        Messenger.default().notify(self.__class__.POST_COMMIT, ldif)

    def _create_server(self, uri, binddn=None, password=None):
        self.server = SynchronousServer(uri[0])
        if binddn is not None:
            self.server.bind(binddn, password)


