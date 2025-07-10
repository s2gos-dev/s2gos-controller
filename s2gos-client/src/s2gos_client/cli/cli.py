#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
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
    from s2gos_client.api.config import ClientConfig

    config = ClientConfig.read()
    if not user_name:
        user_name = click.prompt(
            "User name",
            default=(config and config.user_name)
            or os.environ.get("USER", os.environ.get("USERNAME")),
        )
    if not access_token:
        prev_access_token = config and config.access_token
        _access_token = click.prompt(
            "Access token",
            type=str,
            hide_input=True,
            default="*****" if prev_access_token else None,
        )
        if _access_token == "*****" and prev_access_token:
            access_token = prev_access_token
        else:
            access_token = _access_token
    if not server_url:
        server_url = click.prompt(
            "Server URL",
            default=(config and config.server_url) or DEFAULT_SERVER_URL,
        )
    config_path = ClientConfig(
        user_name=user_name, access_token=access_token, server_url=server_url
    ).write()
    click.echo(f"Configuration written to {config_path}")


@cli.command()
def get_template(
    template_name: str,
    request_file: str = typer.Option(DEFAULT_REQUEST_FILE, "--request"),
):
    """Get a processing request template."""
    click.echo(f"Fetching template {template_name} and writing to {request_file}")


@cli.command()
def list_templates():
    """List available processing request templates."""
    click.echo("Listing available processing request templates")


@cli.command()
def validate_request(name: str = typer.Option(DEFAULT_REQUEST_FILE)):
    """Validate a processing request."""
    click.echo(f"Validating {name}")


@cli.command()
def submit_request(name: str = typer.Option(DEFAULT_REQUEST_FILE)):
    """Submit a processing request."""
    config = _get_config()
    click.echo(f"Submitting request {name} for {config.user_name}")


@cli.command()
def cancel_jobs(job_ids: list[str]):
    """Cancel running processing jobs."""
    config = _get_config()
    click.echo(
        f"Cancelling all jobs of {config.user_name}"
        if not job_ids
        else f"Cancelling jobs {job_ids} of {config.user_name}"
    )


@cli.command()
def poll_jobs(job_ids: list[str]):
    """Poll the status of processing jobs."""
    config = _get_config()
    click.echo(
        f"Polling all jobs of user {config.user_name}"
        if not job_ids
        else f"Polling jobs {job_ids} of {config.user_name}"
    )


@cli.command()
def get_results(job_ids: list[str]):
    """Get processing results."""
    config = _get_config()
    click.echo(f"Getting result of job {job_ids!r} for {config.user_name}")


def _get_config():
    from s2gos_client.api.config import ClientConfig

    config = ClientConfig.read()
    if config is None:
        raise click.ClickException(
            "Tool is not yet configured,"
            " please use the 'configure' command to set it up."
        )
    return config


if __name__ == "__main__":  # pragma: no cover
    cli()
