:mod:`commands` module
======================

The :mod:`commands` module consists of various submodules.

:mod:`core` module
------------------

.. automodule:: ldaptool.commands.core

.. autoclass:: Command
    :members: __init__, call, set_settings, get_settings, _execute,
        _fix_settings, _fix_params

.. autoclass:: ConsoleCommand
    :members: __init__, name, dispatch, option_parser, _option_parser_class,
        _init_option_parser, help

