#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Annotated, Optional

import typer

from s2gos_server.constants import S2GOS_SERVICE_ENV_VAR
from s2gos_server.defaults import DEFAULT_HOST, DEFAULT_PORT

CLI_HELP = """
Server for the ESA synthetic scene generator service DTE-S2GOS.

The server provides a restful API that should be almost compliant
with the OGC API - Processes - Part 1: Core Standard.

For details see https://ogcapi.ogc.org/processes/.

Note that the service parameter may also be given by the 
environment variable `{service_env_var}`.
""".format(
    service_env_var=S2GOS_SERVICE_ENV_VAR,
)


def parse_cli_service_options(
    _ctx: typer.Context, kwargs: Optional[list[str]] = None
) -> list[str]:
    import os
    import shlex

    if not kwargs:
        return []
    service_args = os.environ.get(S2GOS_SERVICE_ENV_VAR)
    if kwargs == [service_args]:
        return shlex.split(service_args)
    return kwargs


cli = typer.Typer(name="s2gos-server", help=CLI_HELP, invoke_without_command=True)

cli_host_option = typer.Option(
    envvar="S2GOS_SERVER_HOST",
    help="Host address.",
)
cli_port_option = typer.Option(
    envvar="S2GOS_SERVER_PORT",
    help="Port number.",
)
cli_service_arg = typer.Argument(
    callback=parse_cli_service_options,
    envvar=S2GOS_SERVICE_ENV_VAR,
    help=(
        "Service instance optionally followed by `--` to pass "
        "service-specific arguments and options."
    ),
)


@cli.callback()
def main(
    _ctx: typer.Context,
    version_: Annotated[
        bool, typer.Option("--version", help="Show version and exit.")
    ] = False,
):
    if version_:
        from importlib.metadata import version

        typer.echo(version("s2gos-server"))
        raise typer.Exit()


@cli.command()
def run(
    host: Annotated[str, cli_host_option] = DEFAULT_HOST,
    port: Annotated[int, cli_port_option] = DEFAULT_PORT,
    service: Annotated[Optional[list[str]], cli_service_arg] = None,
):
    """Run server in production mode."""
    run_server(
        host=host,
        port=port,
        service=service,
        reload=False,
    )


@cli.command()
def dev(
    host: Annotated[str, cli_host_option] = DEFAULT_HOST,
    port: Annotated[int, cli_port_option] = DEFAULT_PORT,
    service: Annotated[Optional[list[str]], cli_service_arg] = None,
):
    """Run server in development mode."""
    run_server(
        host=host,
        port=port,
        service=service,
        reload=True,
    )


def run_server(**kwargs):
    import os
    import shlex

    import uvicorn

    service = kwargs.pop("service", None)
    if isinstance(service, list) and service:
        os.environ[S2GOS_SERVICE_ENV_VAR] = shlex.join(service)

    uvicorn.run("s2gos_server.main:app", **kwargs)


if __name__ == "__main__":  # pragma: no cover
    cli()
