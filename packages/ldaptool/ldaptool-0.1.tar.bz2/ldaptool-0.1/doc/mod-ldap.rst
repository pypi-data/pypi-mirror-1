.. highlight:: python

:mod:`ldaptool.ldap` module -- Manipulate LDAP Databases
========================================================

.. automodule:: ldaptool.ldap

Constants
---------

.. attribute:: SAFE_CHARS

    A collection of characters that are allowed to appear in an LDAP
    attribute. If an attribute contains a character that does not occur in
    the collection, the attribute will be base64 encoded.

    The valid characters are any value <= 127 decimal except NUL, LF, and CR

.. attribute:: SAFE_INIT_CHARS

    A collection of characters that are allowed to appear as the first
    character of an LDAP attribute. If the first character of an attribute
    is a character that does not occur in the collection, the attribute
    will be base64 encoded.

    The valid initial characters are any value <= 127 except NUL, LF, CR,
    SPACE, colon (":", ASCII 58 decimal) and less-than ("<" , ASCII 60
    decimal)


Server connectivity
-------------------

.. autoclass:: Server
    :members:

.. autoclass:: SynchronousServer
    :members:

.. autoclass:: AsynchronousServer
    :members:


LDAP Objects
------------

.. autoclass:: RecordList
    :members:

.. autoclass:: AttrValContainer
    :members:

.. autoclass:: Record
    :members:

.. autoclass:: Entry
    :members:

.. autoclass:: ChangeRecord
    :members:

.. autoclass:: AddChangeRecord
    :members:

.. autoclass:: DeleteChangeRecord
    :members:

.. autoclass:: RenameChangeRecord
    :members:

.. autoclass:: ModifyChangeRecord
    :members:

.. autoclass:: Modification
    :members:

.. autoclass:: AddModification
    :members:

.. autoclass:: DeleteModification
    :members:

.. autoclass:: ReplaceModification
    :members:

