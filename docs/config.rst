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

The precedence rules are very simply

#. Environment
#. ``~/.globus.cfg``
#. ``/etc/globus.cfg``

Config Format
-------------

Config files are INI formatted, so they take the general form

.. code-block:: ini

    [SectionName]
    key1 = value1
    key2 = value2


At present, there are no configuration parameters which you should set in
config files.

The Globus CLI uses the ``[cli]`` section to store configuration information.


Environment Variables
---------------------

``GLOBUS_SDK_ENVIRONMENT`` is a shell variable that can be used to point the
SDK to an alternate set of Globus Servers.

For example, if you have an integration with Globus you may be asked to test
against a preview of upcoming changes. To point the SDK at the Preview environment
``GLOBUS_SDK_ENVIRONMENT=preview`` can be used.
