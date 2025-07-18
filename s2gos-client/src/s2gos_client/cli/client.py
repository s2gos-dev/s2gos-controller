#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Callable, TypeAlias

import typer

from s2gos_client import Client

GetClient: TypeAlias = Callable[[str | None], Client]


def get_client(ctx: typer.Context, config_file: str | None) -> Client:
    _get_client: GetClient = ctx.obj["get_client"]
    return _get_client(config_file)
