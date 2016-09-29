Globus SDK Configuration
========================

There are three standard, canonical locations from which the Globus SDK will
attempt to load configuration.

There are two config file locations:

.. code-block:: shell

    /etc/globus.cfg # system config, shared by all users
    ~/.globus.cfg # personal config, specific to your user

additionally, the shell environment variables loaded into Python's `os.environ`
will be searched for configuration.

Precedence
----------

The precedence rules for config are very simple.
Configuration is loaded with this precendence order

#. Environment
#. ``~/.globus.cfg``
#. ``/etc/globus.cfg``

If a value is defined in ``~/.globus.cfg`` or the environment, it doesn't
matter what it's set to in ``/etc/globus.cfg``.
If a value is defined in the environment, it doesn't matter if it's set in
``~/.globus.cfg`` or ``/etc/globus.cfg``

Config Format
-------------

The format for the configuration files is the same, but of course it will
differ from the way that environment variables are inspected.
Config files are INI formatted, so they take the general form

.. code-block:: ini

    [SectionName1]
    key1 = value1
    key2 = value2

If you don't specify a section name, parsing is permissive and will assume
that you intended your values to be part of the ``general`` section.

So, the following two config files are 100% equivalent:

.. code-block:: ini

    # with a section header!
    [general]
    auth_token = abc123
    transfer_token = def456

.. code-block:: ini

    # no section header!
    auth_token = abc123
    transfer_token = def456

However, the following config file would be invalid because it creates an
ambiguity:

.. code-block:: ini

    # no section header!
    auth_token = abc123
    transfer_token = def456

    # but also a section header!
    [general]
    auth_token = xyz987

    # what value should general:auth_token have?

Environment variables can only modify a value in the ``general`` configuration
section.
They take the form ``GLOBUS_SDK_<uppercase_keyname>``.
For example, ``GLOBUS_SDK_AUTH_TOKEN=abc123`` sets the ``general:auth_token``
value to ``abc123``.

``GLOBUS_SDK_...`` environment variables are very rarely the best way to set a
value, but they let you override values defined in your configuration when
necessary.

There is one very important exception to these rules:
``GLOBUS_SDK_ENVIRONMENT`` is a shell variable that can be used to point the
SDK to an alternate set of Globus Servers.
We currently have plans to create a beta environment that you can use with
``GLOBUS_SDK_ENVIRONMENT=beta`` to get a developer preview of upcoming
features, but this is not available yet. For now, this variable should be left
unset.


Configuration Parameters
------------------------

The following are the configuration parameters you can provide in the config
files, documented in a sample INI file:

.. code-block:: ini

    [general]
    # a token scoped for the Globus Auth service, used by default whenever you
    # instantiate an AuthClient() object
    auth_token = ...
    # a token scoped for the Transfer service, used by default whenever you
    # instantiate an TransferClient() object
    transfer_token = ...
