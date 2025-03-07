.. _tutorial:

Tutorial
========

.. _getting_started:

This is a tutorial in the use of the Globus SDK. It takes you through a simple
step-by-step flow for registering your application, and then using that
registered application to login and interact with services.

These are the steps we will take:

#. :ref:`Create an OAuth2 Client <tutorial_step1>`
#. :ref:`Define your App Object <tutorial_step2>`
#. :ref:`Access the APIs via Clients <tutorial_step3>`

That should be enough to get you up and started.

.. _tutorial_step1:

Step 1: Create an OAuth2 Client
-------------------------------

.. note::

    You can skip this section and jump right in by using the CLIENT_ID seen in
    the example code blocks below! That is the ID of the tutorial client, which
    lets you get started quickly and easily. Come back and create a client of
    your own when you're ready!

Background on OAuth2 Clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Globus uses OAuth2 to handle authentication. In order to login, your
application must be registered with Globus Auth. This is called a "client" in
OAuth2, but Globus will also sometimes call this an "app".

If you plan to create your own application, you should create a new client by
following the instructions below. However, just for the purposes of this
tutorial, we have created a tutorial client which you may use.

In order to complete an OAuth2 flow to get tokens, you must have a client or
"app" definition registered with Globus.

Steps
~~~~~

The following steps will walk you through creating a Native App to be used as your
Globus interaction client.

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

In the rest of the tutorial we will assume in all code samples that the Client UUID is
available in the variable ``CLIENT_ID``.

.. _tutorial_step2:

Step 2: Define your App Object
------------------------------

Accessing Globus APIs as a user requires that you login to your new app and get
it tokens, credentials providing access the service.

Start by defining an application object using ``globus_sdk.UserApp``.

.. code-block:: python

    import globus_sdk

    # this is the tutorial client ID
    # replace this string with your ID for production use
    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"

    # create your app
    my_app = globus_sdk.UserApp("my-user-app", client_id=CLIENT_ID)


.. _tutorial_step3:

Step 3: Access the APIs via Clients
-----------------------------------

Once you have an app defined, you can use it with client objects to access
various Globus APIs.

When you attempt to interact with a service, the app will automatically prompt
you to login.

.. note::

    The default behavior for a ``UserApp`` is to do a CLI-based login flow.
    This behavior can be disabled or customized in numerous ways.

    For the full menu of options, look at the documentation about :ref:`Using a
    GlobusApp! <using_globus_app>`

Start by defining the client object:

.. code-block:: python

    groups_client = globus_sdk.GroupsClient(app=my_app)

And now you can use it to perform some simple interaction, like listing
your groups:

.. code-block:: python

    # print in CSV format
    print("ID,Name,Type,Session Enforcement,Roles")
    for group in groups_client.get_my_groups():
        # parse the group to get data for output
        if group.get("enforce_session"):
            session_enforcement = "strict"
        else:
            session_enforcement = "not strict"
        roles = "|".join({m["role"] for m in group["my_memberships"]})

        print(
            ",".join(
                [
                    group["id"],
                    # note that 'name' could actually have commas in it, so quote it
                    f'"{group["name"]}"',
                    group["group_type"],
                    session_enforcement,
                    roles,
                ]
            )
        )

When ``groups_client.get_my_groups()`` runs in the example above, the SDK
will prompt you to login.

Summary: Complete Examples
--------------------------

For ease of use, here are a pair of examples.

One of them is exactly the same as the tutorial steps above, in a single block.
The other example includes an explicit login step, so you can control when that
login flow happens!

..  tab-set::

    ..  tab-item:: Tutorial Recap

        .. literalinclude:: tutorial_recap.py
            :caption: ``tutorial_recap.py`` [:download:`download <tutorial_recap.py>`]
            :language: python

    ..  tab-item:: Explicit ``login()`` Step

        This example is very similar to the tutorial, but uses a separate login
        step.

        .. literalinclude:: tutorial_with_login_step.py
            :caption: ``tutorial_with_login_step.py`` [:download:`download <tutorial_with_login_step.py>`]
            :language: python

Legacy Tutorial
---------------

The original SDK tutorial is still available as a separate document.
It should only be used for reference for authors who are trying to understand
older projects which predate :class:`GlobusApp`.

.. toctree::
    :caption: Legacy Tutorial
    :maxdepth: 1

    legacy_tutorial
