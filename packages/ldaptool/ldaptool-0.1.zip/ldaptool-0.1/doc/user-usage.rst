.. highlight:: text
.. _usage:

Usage
=====

ldaptool consists of a single binary that is called with the command to be
performed as an argument as in the following::

    ldaptool command [options] [arguments]

The options and arguments are specific to the command used but ldaptool does
take some globally recognized options (see :ref:`generalopts`). These can be
placed before or after the command.

To receive an overview of the commands supported, simply call ldaptool without
and arguments::

    ldaptool

To get detailed information about a subcommand, use the ``help`` command::

    ldaptool help useradd



.. _generalopts:
.. program:: general

General Options
---------------

.. cmdoption:: -f CONFIG, --config CONFIG

    Use the specified file as the configuration file. See :ref:`configuration`
    for more information.

..
    .. cmdoption:: -N, --no-hooks

        Do not run any :ref:`hooks <hooks>`.

.. cmdoption:: --debug

    Enable debugging information



.. _ldapopts:
.. program:: ldap

LDAP Based Commands
-------------------

LDAP based commands manipulate or search the LDAP directory. These commands need
to know a little bit about your infrastructure such as the names of your LDAP
servers. This information can either be defined on the commandline using the
following options or specified in the configuration file (see
:ref:`ldap_settings`).

.. cmdoption:: -D BINDDN, --binddn BINDDN

    Use the Distinguished Name ``BINDDN`` to bind to the LDAP directory. The
    default is to use the value of :conf:`BIND_DN` in the configuration file.

.. cmdoption:: -H LDAPURI, --ldapuri LDAPURI

    URIs of the ldap servers to use. Each URI is separated from the next by a
    coma with no intervening whitespace. The default is to use the value of
    :conf:`LDAP_URI` in the configuration file.

    .. note::
        ldaptool currently only supports one LDAP host. If you specify more than
        one, only the first one will be used.

.. cmdoption:: -w PASSWD, --passwd PASSWD

    Use ``PASSWD`` as the password for authentication. The default is to use
    :conf:`BIND_PASSWD` in the configuration file if it is defined.

.. cmdoption:: -y PASSWD_FILE, --passwd-file PASSWD_FILE

      Use complete contents of ``PASSWD_FILE`` as the password for
      authentication.  The default is to use :conf:`BIND_PASSWD_FILE` in the
      configuration file if it is defined.

.. cmdoption:: -p, --pretend

    Do not actually write any data. This will print the changes that would be
    made and exit.



.. _useradd:
.. program:: useradd

useradd
~~~~~~~

Add a user to the LDAP tree.

::

    ldaptool useradd [options] USER 

The positional argument ``USER`` can either be the full distinguished name of
the user that should be added or only the login name. If a distinguished name is
used, then you must specify the login name using the :option:`-U` option. If you
specify a login name it will be resolved using the :conf:`USER_DN` setting in
the configuration file or the default built-in setting if it is not defined.

Assuming :conf:`USER_DN` is set to ``uid=%(user)s,ou=Users,dc=example,dc=org``
the following two examples perform the exact same action::

    ldaptool useradd jdoe
    ldaptool useradd -U jdoe uid=jdoe,ou=Users,dc=example,dc=org

The reason why the login name  must be explicitly passed using the :option:`-U`
option is because some environments may choose not to use a distinguished name
that includes the login name such as::

    ldaptool useradd -U jdoe -n 'John Doe' cn=John Doe,ou=Users,dc=example,dc=org

Available options:

.. cmdoption:: -c COMMENT, --comment COMMENT

    Any text string. It can be used to specify a short description of the
    account.

.. cmdoption:: -d HOME, --home HOME

    The home directory for the user. The default is to use the :conf:`HOME`
    setting specified in the configuration file. Note that you must use a
    :ref:`hook <hooks>` if you want the directory to be created for you.

.. cmdoption:: -g GROUP, --group GROUP, --gid GROUP

    The group distinguished name, common name or number of the user's initial
    login group. The group name must exist. A group number must refer to an
    existing group. The default is to create a new group with the same name as
    the user's login name.

.. cmdoption:: -G GROUPS, --groups GROUPS

    A list of supplementary groups which the user is also a member of. Each
    group is separated from the next by a colon with no intervening whitespace.
    The groups are subject to the same restrictions as the group given with the
    :option:`-g` option. The default is for the user to belong to no
    supplementary groups.

.. cmdoption:: -U LOGIN, --user LOGIN

    Login name of the user. This option must be specified when using a
    distinguished name as the value for ``USER``.

.. cmdoption:: -m MAIL, --mail MAIL

    E-mail address of the user. The default is to use no e-mail address.

.. cmdoption:: -n NAME, --name NAME

    The name of the user. If the name contains a coma, the part before the coma
    will be used as the surname, the part after as the firstname.

.. cmdoption:: -o, --non-unique

    Allow the creation of a user account with a duplicate (non-unique) UID.

.. cmdoption:: -s SHELL, --shell SHELL

    The name of the user's login shell. The default is to use the :conf:`SHELL`
    setting specified in the configuration file.

.. cmdoption:: -u UID, --uid UID

    The numerical value of the user's ID. This value must be unique, unless the
    :option:`-o` option is used. The value must be non-negative. The default is
    to use the smallest ID value greater than :conf:`UID_MIN` and greater than
    every other user.

See :ref:`ldapopts` for further options that apply to all LDAP manipulating
commands.


.. _groupadd:
.. program:: groupadd

groupadd
~~~~~~~~

Add a group to the LDAP tree.

::

    ldaptool groupadd [options] GROUP

The positional argument ``GROUP`` can either be the full distinguished name of
the group that should be added or only the group name. If a distinguished name
is used, then you must specify the group name using the :option:`-G`
option. If you specify a group name it will be resolved using the
:conf:`GROUP_DN` setting in the configuration file or the default built-in
setting if it is not defined.

Assuming :conf:`GROUP_DN` is set to ``cn=%(group)s,ou=Groups,dc=example,dc=org``
the following two examples perform the exact same action::

    ldaptool groupadd admins
    ldaptool groupadd -G admins cn=admins,ou=Groups,dc=example,dc=org

Available options:

.. cmdoption:: -c COMMENT, --comment COMMENT

    Any text string. It can be used to specify a short description of the
    group.

.. cmdoption:: -g GID, --gid GID

    The numerical value of the group's ID. This value must be unique unless the
    :option:`-o` option is used. The value must be non-negative. The
    default is to use the first available available value between
    :conf:`GID_MIN` and :conf:`GID_MAX` as defined in the configuration file.

.. cmdoption:: -G GROUP, --group GROUP

    Name of the group. This option must be specified when using a distinguished
    name as the value for ``GROUP``.

.. cmdoption:: -o, --non-unique

    Allow the creation of a group with a duplicate (non-unique) GID.

See :ref:`ldapopts` for further options that apply to all LDAP manipulating
commands.



.. _userdel:
.. program:: userdel

userdel
~~~~~~~

Delete a user.

::

    ldaptool userdel [options] USER

The positional argument ``USER`` can either be the full distinguished name of
the user that should be removed or only the user name.

This command provides no additional options. See :ref:`ldapopts` for options
that apply to all LDAP manipulating commands.



.. _groupdel:
.. program:: groupdel

groupdel
~~~~~~~~

Delete a group.

::

    ldaptool groupdel [options] GROUP

The positional argument ``GROUP`` can either be the full distinguished name of
the group that should be removed or only the group name.

This command provides no additional options. See :ref:`ldapopts` for options
that apply to all LDAP manipulating commands.


