#  Copyright (c) 2025-2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Final

from pathlib import Path

import typer
from typer.cli import get_docs_for_click
from typer.main import get_command

from gavicore.util.dynimp import import_value

from tools.common import S2GOS_PATH

DOCS_PATH: Final = S2GOS_PATH / "docs"

TOOL_CONFIG = [
    ["S2GOS Client CLI", "s2gos_client.cli:cli", DOCS_PATH / "client-cli.md"],
    [
        "S2GOS Server CLI",
        "s2gos_server.cli:cli",
        DOCS_PATH / "server-cli.md",
    ],
]


def generate_cli_docs():
    for title, app_ref, target_path in TOOL_CONFIG:
        print(f"Writing docs for {title} to {target_path}")

        app = import_value(app_ref, type=typer.Typer, name="app_ref")

        click_obj = get_command(app)
        ctx = typer.Context(click_obj)

        docs = get_docs_for_click(
            obj=click_obj,
            ctx=ctx,
            title=title,
        )

        Path(target_path).write_text(f"{docs.strip()}\n", encoding="utf-8")


if __name__ == "__main__":
    # noinspection PyTypeChecker
    generate_cli_docs()
