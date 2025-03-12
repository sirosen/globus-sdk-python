.. _tutorials:

.. _getting_started:

Getting Started
===============

These docs cover basic usage of the Globus SDK.

They takes you through a simple step-by-step flow for registering your
application, and then using that registered application to login and
interact with services.

Two example scripts are offered -- one using the ``GlobusApp`` class and one
without it. ``GlobusApp`` is recommended for most use cases, but there are
scenarios which are not supported by it. Reading the non-``GlobusApp`` example
may also enhance your understanding of how ``GlobusApp`` works.

.. toctree::
    :caption: How To Use the SDK
    :maxdepth: 1

    Register an App in Globus Auth <register_app>
    Create a Minimal Script <minimal_script>
    Create a Script Without GlobusApp <minimal_script_noapp>
