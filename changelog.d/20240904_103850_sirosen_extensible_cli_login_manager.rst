Changed
~~~~~~~

.. rubric:: Experimental

-   The ``CommandLineLoginFlowManager`` now exposes ``print_authorize_url`` and
    ``prompt_for_code`` as methods, which replace the ``login_prompt`` and
    ``code_prompt`` parameters. Users who wish to customize prompting behavior
    now have a greater degree of control, and can effect this by subclassing the
    ``CommandLineLoginFlowManager``. (:pr:`1039`)

    Example usage, which uses the popular ``click`` library to handle the
    prompts:

    .. code-block:: python

        import click
        from globus_sdk.experimental.login_flow_manager import CommandLineLoginFlowManager


        class ClickLoginFlowManager(CommandLineLoginFlowManager):
            def print_authorize_url(self, authorize_url: str) -> None:
                click.echo(click.style("Login here for a code:", fg="yellow"))
                click.echo(authorize_url)

            def prompt_for_code(self) -> str:
                return click.prompt("Enter the code here:")
