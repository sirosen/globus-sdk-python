Welcome to ``globus_sdk._testing``
==================================

.. warning::

    Use at your own risk! This subpackage is highly experimental. It may
    feature breaking changes to the data and the interfaces without prior
    notice.

This is an experimental internal module offered by the Globus SDK to share
API fixtures for use with the ``responses`` library.

Dependencies
------------

This toolchain requires the ``responses`` library.

If you are using ``_testing``, it is recommended that you use the same version of
``responses`` that the globus-sdk uses. At time of writing, ``responses==0.17.0``.

Recommended Fixtures
--------------------

Under pytest, this is the recommended fixture for setting up responses and
guaranteeing that requests are sent to the production hostnames:

.. code-block:: python

    @pytest.fixture(autouse=True)
    def mocked_responses(monkeypatch):
        responses.start()
        monkeypatch.setitem(os.environ, "GLOBUS_SDK_ENVIRONMENT", "production")
        yield
        responses.stop()
        responses.reset()

Usage
-----

Once ``responses`` has been activated, each fixture can be loaded and activated
by name:

.. code-block:: python

    from globus_sdk._testing import load_fixture

    load_fixture("auth.get_identities")
    # "case" is used to have a single name map to multiple fixtures
    data = load_fixture("auth.get_identities", case="multiple")

Some sets of fixtures may describe a scenario, and therefore it's desirable to
load all of them at once:

.. code-block:: python

    from globus_sdk._testing import load_fixture

    fixtures = load_fixture_set("foo.bar")
    fixtures.activate_all()
