.. highlight:: python

.. _configuration:

Configuration
=============

The ldaptool configuration file allows you to customize how ldaptool works.
Although ldaptool is designed to work without any such configuration file, you
will most certainly not be satisfied with its default behavior and will
therefore want to create such a file.

You can specify the configuration file using the :option:`-f` option.
Alternatively, ldaptool will try to load the configuration from `~/.ldaptool`
or `/etc/ldaptool` if the files exist.


General Settings
----------------

..
    .. config:: HOOKS

        Hooks allow you to define additional actions that should be performed during
        the usage of ldaptool. For example, you can create a user's home directory
        after a successfull useradd or clean up after a userdel.

        .. example::
            :comment:

            HOOKS=(
                ('useradd.post', 'mkdir', {
                    'path': "/home/%(user)s",
                    'skel': "/etc/skel",
                    'owner': "%(user)s",
                    'group': "%(group)s",
                }),
                ('useradd.post', 'mkdir', {
                    'path': "/var/spool/%(user)s",
                    'owner': "%(user)s",
                    'group': "mail",
                    'umask': 0007,
                }),
                ('userdel.post', 'rm', {'path': "/home/%(user)s"}),
                ('userdel.post', 'rm', {'path': "/var/spool/%(user)s"}),
            )

.. config:: COMMANDS

    Select commands that ldaptool should support.

    This allows you to add additional commands or suppress unwanted ones. If
    this is not defined, the built-in default set of commands will be used.

    .. example::
        :comment:

        COMMANDS=(
            'ldaptool.commands.Help',
            'ldaptool.commands.Useradd',
            'ldaptool.commands.Userdel',
            'ldaptool.commands.Usermod',
            'ldaptool.commands.Groupadd',
            'ldaptool.commands.Groupdel',
            'ldaptool.commands.Groupmod',
            'ldaptool.commands.Password',
        )

..
    .. config:: HOOK_COMMANDS

        Additional commands that ldaptool should support for hooks.

        You only need to list commands that are not already listed under
        :conf:`COMMANDS`. If this is not defined, the default built-in set of hook
        commands will be used.

        .. example::
            :comment:

            HOOK_COMMANDS=(
                'ldaptool.commands.Makedir',
                'ldaptool.commands.Remove',
            )


.. _ldap_settings:

LDAP Settings
-------------

.. config:: LDAP_URI

    URIs of the LDAP servers to be used. You can list as many servers as you
    like.

    .. note::
        ldaptool currently only supports one LDAP host. If you specify more than
        one, only the first one will be used.

    .. example::
        
        LDAP_URI=["ldap://ladp01.example.org", "ldap://ldap02.example.org"]

    .. seealso::
        :rfc:`4516` - Lightweight Directory Access Protocol (LDAP): Uniform
        Resource Locator

.. config:: LDAP_BASE

    Base to be the starting point for searches and modifications on the LDAP
    directory.

    .. example::

        LDAP_BASE="dc=example,dc=org"

.. config:: BIND_DN

    The Distinguished Name to be used to bind to the LDAP directory. 

    .. example::
        :comment:

        BIND_DN="cn=admin,dc=example,dc=org"

.. config:: BIND_PASSWD

    Password for simple authentication.

    Currently ldaptool only supports simple authentication and not SASL. If both
    :conf:`BIND_PASSWD` and :conf:`BIND_PASSWD_FILE` are defined,
    :conf:`BIND_PASSWD` will take precedence.

    .. example::
        :comment:

        BIND_PASSWD="secret"

.. config:: BIND_PASSWD_FILE

    Use complete contents of the specified file as the password for simple
    authentication.

    Currently ldaptool only supports simple authentication and not SASL. If both
    :conf:`BIND_PASSWD` and :conf:`BIND_PASSWD_FILE` are defined,
    :conf:`BIND_PASSWD` will take precedence.

    .. example::
        :comment:

        BIND_PASSWD_FILE="/etc/ldap.secret"

Accounts
--------

.. config:: USER_DN

    The Distinguished Name at which a user can be found if only the user name
    is given.

    .. example::
        :comment:

        USER_DN="uid=%(user)s,ou=Users,%(basedn)s"

.. config:: GROUP_DN

    The Distinguished Name at which a group can be found if only the group name
    is given.

    .. example::
        :comment:

        GROUP_DN="cn=%(group)s,ou=Groups,%(basedn)s"

Useradd
-------

.. config:: UID_MIN

    Minimum value for automatic uid selection.

    .. example::

        UID_MIN=1000

.. config:: UID_MAX

    Maximum value for automatic uid selection.

    .. example::

        UID_MAX=60000

.. config:: HOME

    Default home path.

    .. example::

        HOME="/home/%(user)s"

.. config:: SHELL

    Default login shell.

    .. example::

        SHELL="/bin/bash"

Groupadd
--------

.. config:: GID_MIN

    Minimum value for automatic gid selection.

    .. example::

        GID_MIN=100

.. config:: GID_MAX

    Maximum value for automatic gid selection.

    .. example::

        GID_MAX=60000

