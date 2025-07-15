#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
from pathlib import Path
from typing import Optional

import click
import typer.core

from s2gos_client.api.defaults import DEFAULT_REQUEST_FILE, DEFAULT_SERVER_URL


class AliasedGroup(typer.core.TyperGroup):
    @staticmethod
    def to_alias(name: str):
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


HELP = """
Client tool for the ESA synthetic scene generator service DTE-S2GOS.

The tool provides commands for managing processing request templates,
processing requests, processing jobs, and gets processing results.

You can use shorter command name aliases, e.g., use command name "vr"
instead of "validate-request", or "lt" instead of "list-templates".
"""

cli = typer.Typer(name="s2gos-client", cls=AliasedGroup, help=HELP)


@cli.command()
def configure(
    user_name: Optional[str] = typer.Option(None, "--user"),
    access_token: Optional[str] = typer.Option(None, "--token"),
    server_url: Optional[str] = typer.Option(None, "--url"),
):
    """Configure the S2GOS client."""
    from .impl import configure_client

    configure_client(
        user_name=user_name, access_token=access_token, server_url=server_url
    )


@cli.command()
def list_processes():
    """List available processes."""
    from .impl import get_client, render_process_list

    process_list = get_client().get_processes()
    render_process_list(process_list)


@cli.command()
def get_process(process_id: str):
    """Get process details."""
    from .impl import get_client, render_process_description

    process_description = get_client().get_process(process_id)
    render_process_description(process_description)


@cli.command()
def validate_request(request_file: str = typer.Option(DEFAULT_REQUEST_FILE)):
    """Validate a processing request."""
    from .impl import read_request

    _request = read_request(request_file)
    click.echo(f"Request {request_file} is valid.")


@cli.command()
def execute_process(request_file: str = typer.Option(DEFAULT_REQUEST_FILE)):
    """Execute a process."""
    from .impl import read_request, get_client, render_job

    request = read_request(request_file)
    job = get_client().execute_process(
        process_id=request.process_id, request=request.request
    )
    render_job(job)


@cli.command()
def list_jobs():
    """List jobs."""
    from .impl import get_client, render_job_list

    job_list = get_client().get_jobs()
    render_job_list(job_list)


@cli.command()
def get_job(job_id: str):
    """Cancel running processing jobs."""
    from .impl import get_client, render_job

    job = get_client().get_job(job_id)
    render_job(job)


@cli.command()
def dismiss_job(job_id: str):
    """Cancel a running or delete a finished job."""
    from .impl import get_client, render_job

    job = get_client().dismiss_job(job_id)
    render_job(job)


@cli.command()
def get_job_results(job_id: str):
    """Get processing results."""
    from .impl import get_client, render_job_results

    job_results = get_client().get_job_results(job_id)
    render_job_results(job_results)


if __name__ == "__main__":  # pragma: no cover
    cli()
