.. _tutorial_register_app:

Registering a Globus Auth App
=============================

An OAuth2 Client, also sometimes called an "app", represents an application or
script.

When a user logs in to an application, they grant consent for the client to
perform certain actions, and the client is issued appropriate credentials for
those actions.

Having your own app registered with the service also lets you set certain app-level
settings for user logins, and keeps your application isolated from everyone
else's apps using the service.

.. note::

    SDK Tutorials and Examples frequently make use of the "tutorial client ID".
    This makes the examples work if you copy and run them, but using the
    tutorial client for production use cases is not recommended or supported.

Developers who wish to learn more about OAuth2 at Globus are encouraged to read
the `Clients, Scopes, and Consents
<https://docs.globus.org/guides/overviews/clients-scopes-and-consents/>`_
documentation.

App Types & Native App
----------------------

There are several different types of applications which you can register with
Globus Auth.

For simplicity, this tutorial will only cover how to create a
"Native App" -- this is the suitable type of application for scripts and
distributed applications which can't have a secret associated with them.

Creating a Native App
---------------------

1. Navigate to the `Developer Site <https://app.globus.org/settings/developers>`_

2. Select "Register a thick client or script that will be installed and run by users on
   their devices."

3. Create or Select a Project

   * A project is a collection of apps with a shared list of administrators.
   * If you don't own any projects, you will automatically be prompted to create one.
   * If you do, you will be prompted to either select an existing or create a new one.

4. Creating or selecting a project will prompt you for another login, sign in with an
   account that administers your project.

5. Give your App a name; this is what users will see when they are asked to
   authorize your app.

6. Click "Register App". This will create your app and take you to a page
   describing it.

7. Copy the "Client UUID" from the page.

   * This ID can be thought of as your App's "username". It is non-secure information
     and as such, feel free to hardcode it into scripts.

.. note::

    In many tutorials and code samples we assume that the Client UUID is available
    in the variable ``CLIENT_ID``.

    In many cases, you can copy down code samples and plug in your Client UUID
    and the examples will work without further modification!
