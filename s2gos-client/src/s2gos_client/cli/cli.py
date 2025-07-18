#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Annotated, Final, Optional

import click
import typer.core

from s2gos_client.cli.aliased_group import AliasedGroup
from s2gos_client.cli.output import OutputFormat

SERVICE_NAME = "S2GOS service"

CLI_NAME = "s2gos-client"
CLI_HELP = """
Client tool for the {service_name}.

The tool provides commands for managing processing request templates,
processing requests, processing jobs, and gets processing results.

You can use shorter command name aliases, e.g., use command name "vr"
for "validate-request", or "lp" for "list-processes".
""".format(service_name=SERVICE_NAME)

DEFAULT_OUTPUT_FORMAT: Final = OutputFormat.yaml
DEFAULT_REQUEST_FILE: Final = "process-request.yaml"

process_id_arg = typer.Argument(
    help="Process identifier",
)

job_id_arg = typer.Argument(
    help="Job identifier",
)

config_option = typer.Option(
    ...,
    "--config",
    "-c",
    help="Client configuration file",
    metavar="PATH",
)

request_option = typer.Option(
    ...,
    "--request",
    "-r",
    help="Processing request file",
    metavar="PATH",
)

format_option = typer.Option(
    ...,
    "--format",
    "-f",
    show_choices=True,
    help="Output format",
    # metavar="FORMAT",
)

cli = typer.Typer(
    name=CLI_NAME,
    cls=AliasedGroup,
    help=CLI_HELP,
    invoke_without_command=True,
    # no_args_is_help=True,  # check: it shows empty error msg
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

    def get_client(config_path: str | None):
        # defer importing
        from s2gos_client import Client
        from s2gos_client.cli.config import read_config

        config = read_config(config_path)
        return Client(config=config)

    ctx.ensure_object(dict)
    # ONLY set context values if they haven't already been set,
    # e.g., by a test
    for k, v in dict(
        get_client=get_client,
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
    from .config import configure_client

    configure_client(
        user_name=user_name, access_token=access_token, server_url=server_url
    )


@cli.command()
def list_processes(
    ctx: typer.Context,
    config_file: Annotated[str, config_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """List available processes."""
    from .client import get_client
    from .output import get_renderer

    process_list = get_client(ctx, config_file).get_processes()
    get_renderer(output_format).render_process_list(process_list)


@cli.command()
def get_process(
    ctx: typer.Context,
    process_id: Annotated[str, process_id_arg],
    config_file: Annotated[Optional[str], config_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Get process details."""
    from .client import get_client
    from .output import get_renderer

    process_description = get_client(ctx, config_file).get_process(process_id)
    get_renderer(output_format).render_process_description(process_description)


@cli.command()
def validate_request(
    process_id: Annotated[
        Optional[str], typer.Argument(help="Process identifier")
    ] = None,
    parameters: Annotated[
        Optional[list[str]],
        typer.Argument(help="Parameters", metavar="[NAME=VALUE]..."),
    ] = None,
    request_file: Annotated[Optional[str], request_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """
    Validate a processing request.

    The `--request` option and the `process_id` argument are mutually exclusive.
    """
    from .output import get_renderer
    from .request import read_processing_request

    request = read_processing_request(process_id, parameters, request_file)
    get_renderer(output_format).render_processing_request_valid(
        request, source=request_file
    )


@cli.command()
def execute_process(
    ctx: typer.Context,
    process_id: Annotated[
        Optional[str], typer.Argument(help="Process identifier")
    ] = None,
    parameters: Annotated[
        Optional[list[str]],
        typer.Argument(help="Parameters", metavar="[NAME=VALUE]..."),
    ] = None,
    request_file: Annotated[str, request_option] = DEFAULT_REQUEST_FILE,
    config_file: Annotated[str, config_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Execute a process."""
    from .client import get_client
    from .output import get_renderer
    from .request import read_processing_request

    request = read_processing_request(process_id, parameters, request_file)
    job = get_client(ctx, config_file).execute_process(
        process_id=request.process_id, request=request.as_process_request()
    )
    get_renderer(output_format).render_job(job)


@cli.command()
def list_jobs(
    ctx: typer.Context,
    config_file: Annotated[str, config_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """List all jobs."""
    from .client import get_client
    from .output import get_renderer

    job_list = get_client(ctx, config_file).get_jobs()
    get_renderer(output_format).render_job_list(job_list)


@cli.command()
def get_job(
    ctx: typer.Context,
    job_id: Annotated[str, job_id_arg],
    config_file: Annotated[Optional[str], config_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Get job details."""
    from .client import get_client
    from .output import get_renderer

    job = get_client(ctx, config_file).get_job(job_id)
    get_renderer(output_format).render_job(job)


@cli.command()
def dismiss_job(
    ctx: typer.Context,
    job_id: Annotated[str, job_id_arg],
    config_file: Annotated[str, config_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Cancel a running or delete a finished job."""
    from .client import get_client
    from .output import get_renderer

    job = get_client(ctx, config_file).dismiss_job(job_id)
    get_renderer(output_format).render_job(job)


@cli.command()
def get_job_results(
    ctx: typer.Context,
    job_id: Annotated[str, job_id_arg],
    config_file: Annotated[str, config_option] = None,
    output_format: Annotated[OutputFormat, format_option] = DEFAULT_OUTPUT_FORMAT,
):
    """Get job results."""
    from .client import get_client
    from .output import get_renderer

    job_results = get_client(ctx, config_file).get_job_results(job_id)
    get_renderer(output_format).render_job_results(job_results)


if __name__ == "__main__":  # pragma: no cover
    cli()
