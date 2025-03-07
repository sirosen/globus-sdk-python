.. _minimal_app_tutorial:

Tutorial: A Minimal App
=======================

This is a basic tutorial in the use of the Globus SDK.

#. :ref:`Create an OAuth2 Client <minimal_app_createclient>`
#. :ref:`Define your App Object <minimal_app_defineapp>`
#. :ref:`Access the APIs via Clients <minimal_app_useclients>`

.. _minimal_app_createclient:

Create an OAuth2 Client
-----------------------

You can jump right in by using the ``CLIENT_ID`` seen in the example code blocks below!
That is the ID of the tutorial client, which lets you get started quickly and easily.

When you are ready to create your own application, follow :ref:`the tutorial on
registering a Native App <tutorial_register_app>` and use its ``CLIENT_ID`` in
the rest of the tutorial to get your own app setup.

.. _minimal_app_defineapp:

Define your App Object
----------------------

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


.. note::

    The default behavior for a ``UserApp`` is to do a CLI-based login flow.
    This behavior can be disabled or customized in numerous ways.

    For the full menu of options, look at the documentation about :ref:`Using a
    GlobusApp! <using_globus_app>`

.. _minimal_app_useclients:

Access the APIs via Clients
---------------------------

Once you have an app defined, you can use it with client objects to access
various Globus APIs.

When you attempt to interact with a service, the app will automatically prompt
you to login.

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

*These examples are complete. They should run without errors "as is".*

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
