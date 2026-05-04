#  Copyright (c) 2026 by the Eozilla team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from pathlib import Path
from typing import Annotated

import panel as pn
import typer


from s2gos_client.gui import ClientConfig
from gavicore.ui.panel.schema2ui import schemas_to_ui


pn.extension()

DEFAULT_SCHEMAS_DIR = Path(__file__).parent / "schemas"

APP_NAME = "schema2ui"

app = typer.Typer()


@app.command(name=APP_NAME)
def main(
    schemas: Annotated[
        list[str],
        typer.Argument(
            help="Path to the schema YAML file or a known schema name.",
            default_factory=lambda: [DEFAULT_SCHEMAS_DIR],
        ),
    ],
) -> None:
    """Convert a selected schema into a Panel UI."""
    schemas_to_ui(
        *schemas, registry=ClientConfig.default_config.get_field_factory_registry()
    )


if __name__ == "__main__":
    app()
