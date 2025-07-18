#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Optional, Callable, Annotated

import click
import typer.core

from s2gos_client.cli.aliased_group import AliasedGroup
from s2gos_client.cli.defaults import DEFAULT_OUTPUT_FORMAT
from s2gos_client.cli.defaults import DEFAULT_REQUEST_FILE
from s2gos_client.cli.defaults import OutputFormat


SERVICE_NAME = "S2GOS service"

CLI_NAME = "s2gos-client"
CLI_HELP = """
Client tool for the {service_name}.

The tool provides commands for managing processing request templates,
processing requests, processing jobs, and gets processing results.

You can use shorter command name aliases, e.g., use command name "vr"
for "validate-request", or "lp" for "list-processes".
""".format(service_name=SERVICE_NAME)

process_id_arg = typer.Argument(
    help="Process identifier",
)

job_id_arg = typer.Argument(
    help="Job identifier",
)

request_option = typer.Option(
    ...,
    "--request",
    "-r",
    help="Processing request file",
)

format_option = typer.Option(
    ...,
    "--format",
    "-f",
    show_choices=True,
    help="Output format",
)


cli = typer.Typer(
    name=CLI_NAME, cls=AliasedGroup, help=CLI_HELP, invoke_without_command=True
)


@cli.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool, typer.Option("--version", help="Show version and exit")
    ] = False,
    # add global options here...
    # verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    if version:
        from importlib.metadata import version

        click.echo(version("s2gos-client"))
        return

    def _get_client():
        # defer importing
        from s2gos_client.cli.impl import get_client

        return get_client()

    ctx.ensure_object(dict)
    # ONLY set context values if they haven't already been set,
    # e.g., by a test
    for k, v in dict(
        get_client=_get_client,
        # add global options here...
        # verbose=verbose,
    ).items():
        if k not in ctx.obj:
            ctx.obj[k] = v


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
    ctx: typer.Context,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """List available processes."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    process_list = get_client().get_processes()
    OutputRenderer.get(output_format).render_process_list(process_list)


@cli.command()
def get_process(
    ctx: typer.Context,
    process_id: Annotated[str, process_id_arg],
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Get process details."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    process_description = get_client().get_process(process_id)
    OutputRenderer.get(output_format).render_process_description(process_description)


@cli.command()
def validate_request(
    request_file: Annotated[str, request_option] = DEFAULT_REQUEST_FILE,
):
    """Validate a processing request."""
    from .impl import read_request

    _request = read_request(request_file)
    click.echo(f"Request {request_file} is valid.")


@cli.command()
def execute_process(
    ctx: typer.Context,
    request_file: Annotated[str, request_option] = DEFAULT_REQUEST_FILE,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
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
    ctx: typer.Context,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """List all jobs."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job_list = get_client().get_jobs()
    OutputRenderer.get(output_format).render_job_list(job_list)


@cli.command()
def get_job(
    ctx: typer.Context,
    job_id: Annotated[str, job_id_arg],
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Get job details."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job = get_client().get_job(job_id)
    OutputRenderer.get(output_format).render_job(job)


@cli.command()
def dismiss_job(
    ctx: typer.Context,
    job_id: Annotated[str, job_id_arg],
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Cancel a running or delete a finished job."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job = get_client().dismiss_job(job_id)
    OutputRenderer.get(output_format).render_job(job)


@cli.command()
def get_job_results(
    ctx: typer.Context,
    job_id: Annotated[str, job_id_arg],
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Get job results."""
    from .renderer import OutputRenderer

    get_client: Callable = ctx.obj["get_client"]
    job_results = get_client().get_job_results(job_id)
    OutputRenderer.get(output_format).render_job_results(job_results)


if __name__ == "__main__":  # pragma: no cover
    cli()
