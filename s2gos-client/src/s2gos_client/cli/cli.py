#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Optional, Callable, Annotated

import click
import typer.core

from s2gos_client.cli.renderer import OutputFormat
from s2gos_client.cli.defaults import DEFAULT_OUTPUT_FORMAT
from s2gos_client.cli.defaults import DEFAULT_REQUEST_FILE


SERVICE_NAME = "S2GOS service"
CLI_NAME = "s2gos-client"
CLI_HELP = """
Client tool for the {service_name}.

The tool provides commands for managing processing request templates,
processing requests, processing jobs, and gets processing results.

You can use shorter command name aliases, e.g., use command name "vr"
for "validate-request", or "lp" for "list-processes".
""".format(service_name=SERVICE_NAME)


job_id_arg = typer.Argument(
    help="Job identifier",
)

request_option = typer.Option(
    DEFAULT_REQUEST_FILE,
    "--request",
    "-r",
    help="Processing request file",
)

format_option = typer.Option(
    DEFAULT_OUTPUT_FORMAT,
    "--format",
    "-f",
    show_choices=True,
    help="Output format",
)


class AliasedGroup(typer.core.TyperGroup):
    """
    A group that accepts command aliases created from the
    first letters of the words after splitting a command name
    at hyphens.
    """

    @staticmethod
    def to_alias(name: str):
        """Create a short alias for given command name."""
        return "".join(map(lambda n: n[0], name.split("-")))

    def get_command(self, ctx, cmd_name):
        rv = super().get_command(ctx, cmd_name)

        if rv is not None:
            return rv

        matches = [
            x
            for x in self.list_commands(ctx)
            if cmd_name == x or cmd_name == self.to_alias(x)
        ]

        if not matches:
            return None

        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(
        self, ctx, args
    ) -> tuple[str | None, click.Command | None, list[str]]:
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        if cmd is not None:
            return cmd.name, cmd, args
        else:
            return None, None, args

    def list_commands(self, ctx):
        # prevent alphabetical ordering
        return list(self.commands)


cli = typer.Typer(name=CLI_NAME, cls=AliasedGroup, help=CLI_HELP)


def _get_client():
    # defer importing
    from s2gos_client.cli.impl import get_client

    return get_client()


@cli.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    ctx.ensure_object(dict)
    # ONLY set context values if they haven't already been set,
    # e.g., by a test
    for k, v in dict(get_client=_get_client, verbose=verbose).items():
        if k not in ctx.obj:
            ctx.obj[k] = v


@cli.command()
def version():
    """Show version and exit."""
    from importlib.metadata import version

    click.echo(version("s2gos-client"))


@cli.command()
def configure(
    user_name: Optional[str] = typer.Option(None, "--user"),
    access_token: Optional[str] = typer.Option(None, "--token"),
    server_url: Optional[str] = typer.Option(None, "--url"),
):
    """Configure the client tool."""
    from .impl import configure_client

    configure_client(
        user_name=user_name, access_token=access_token, server_url=server_url
    )


@cli.command()
def list_processes(
    ctx: typer.Context, output_format: Annotated[OutputFormat, format_option]
):
    """List available processes."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    process_list = get_client().get_processes()
    OutputRenderer.get(output_format).render_process_list(process_list)


@cli.command()
def get_process(
    ctx: typer.Context,
    process_id: str,
    output_format: Annotated[OutputFormat, format_option],
):
    """Get process details."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    process_description = get_client().get_process(process_id)
    OutputRenderer.get(output_format).render_process_description(process_description)


@cli.command()
def validate_request(
    request_file: Annotated[str, request_option],
):
    """Validate a processing request."""
    from .impl import read_request

    _request = read_request(request_file)
    click.echo(f"Request {request_file} is valid.")


@cli.command()
def execute_process(
    ctx: typer.Context,
    request_file: Annotated[str, request_option],
    output_format: Annotated[OutputFormat, format_option],
):
    """Execute a process."""
    from .impl import read_request
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    request = read_request(request_file)
    job = get_client().execute_process(
        process_id=request.process_id, request=request.request
    )
    OutputRenderer.get(output_format).render_job(job)


@cli.command()
def list_jobs(
    ctx: typer.Context, output_format: Annotated[OutputFormat, format_option]
):
    """List all jobs."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job_list = get_client().get_jobs()
    OutputRenderer.get(output_format).render_job_list(job_list)


@cli.command()
def get_job(
    ctx: typer.Context,
    job_id: str,
    output_format: Annotated[OutputFormat, format_option],
):
    """Get job details."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job = get_client().get_job(job_id)
    OutputRenderer.get(output_format).render_job(job)


@cli.command()
def dismiss_job(
    ctx: typer.Context,
    job_id: str,
    output_format: Annotated[OutputFormat, format_option],
):
    """Cancel a running or delete a finished job."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job = get_client().dismiss_job(job_id)
    OutputRenderer.get(output_format).render_job(job)


@cli.command()
def get_job_results(
    ctx: typer.Context,
    job_id: str,
    output_format: Annotated[OutputFormat, format_option],
):
    """Get job results."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job_results = get_client().get_job_results(job_id)
    OutputRenderer.get(output_format).render_job_results(job_results)


if __name__ == "__main__":  # pragma: no cover
    cli()
