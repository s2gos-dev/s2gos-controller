#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from types import TracebackType
from typing import Callable, Literal, Optional, TypeAlias

import click
import typer

from s2gos_client.api.client import Client
from s2gos_client.api.error import ClientError

GetClient: TypeAlias = Callable[[str | None], Client]


def get_client(ctx: typer.Context, config_file: str | None) -> Client:
    _get_client: GetClient = ctx.obj["get_client"]
    return _get_client(config_file)


def use_client(ctx: typer.Context, config_file: str | None) -> "UseClient":
    return UseClient(ctx, config_file)


class UseClient:
    def __init__(self, ctx: typer.Context, config_file: str | None):
        self.ctx = ctx
        self.config_file = config_file
        self.client: Client | None = None

    def __enter__(self):
        _get_client: GetClient = self.ctx.obj["get_client"]
        self.client = _get_client(self.config_file)
        return self.client

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Literal[False]:
        if self.client is not None:
            self.client.close()
            self.client = None
        if isinstance(exc_value, ClientError):
            client_error: ClientError = exc_value
            message: str | None = client_error.detail or client_error.title
            raise click.ClickException(
                f"{message} ({client_error})"
                if message
                else f"Server error ({client_error})"
            )
        return False
