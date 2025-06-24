#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
from typing import Optional

import typer
from s2gos_server import __version__
from s2gos_server.constants import S2GOS_SERVICE_ENV_VAR
from s2gos_server.defaults import DEFAULT_HOST, DEFAULT_PORT

cli = typer.Typer()


@cli.command()
def version():
    """Show server version."""
    typer.echo(f"Version {__version__}")


@cli.command()
def run(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    service: Optional[str] = None,
):
    """Run server in production mode."""
    run_server(host=host, port=port, service=service, reload=False)


@cli.command()
def dev(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    service: Optional[str] = None,
):
    """Run server in development mode."""
    run_server(host=host, port=port, service=service, reload=True)


def run_server(**kwargs):
    import uvicorn

    service_ref = kwargs.pop("service", None)
    if isinstance(service_ref, str) and service_ref:
        os.environ[S2GOS_SERVICE_ENV_VAR] = service_ref

    uvicorn.run("s2gos_server.main:app", **kwargs)


if __name__ == "__main__":  # pragma: no cover
    cli()
