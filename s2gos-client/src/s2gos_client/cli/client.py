#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from types import TracebackType
from typing import Callable, Literal, Optional, TypeAlias

import click
import typer

from s2gos_client.api.client import Client
from s2gos_client.api.exceptions import ClientException

GetClient: TypeAlias = Callable[[str | None], Client]


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
        show_traceback = self.ctx.obj.get("traceback", False)
        if isinstance(exc_value, ClientException):
            client_error: ClientException = exc_value
            api_error = client_error.api_error
            message_lines = [
                f"{client_error}",
                "Server-side error details:",
                f"  title:  {api_error.title}",
                f"  status: {api_error.status}",
                f"  type:   {api_error.type}",
                f"  detail: {api_error.detail}",
            ]
            if api_error.traceback and show_traceback:
                message_lines.append("  traceback:")
                message_lines.extend(api_error.traceback)
            raise click.ClickException("\n".join(message_lines))
        return False
