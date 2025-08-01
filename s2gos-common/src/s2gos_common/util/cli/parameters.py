#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import typer

# See also s2gos-client/src/s2gos_client/cli/cli.py
PROCESS_ID_ARGUMENT = typer.Argument(
    help="Process identifier.",
)

# See also s2gos-client/src/s2gos_client/cli/cli.py
REQUEST_INPUT_OPTION = typer.Option(
    "--input",
    "-i",
    help="Process input value.",
    metavar="[NAME=VALUE]...",
)

# See also s2gos-client/src/s2gos_client/cli/cli.py
REQUEST_SUBSCRIBER_OPTION = typer.Option(
    "--subscriber",
    "-s",
    help="Process subscriber URL.",
    metavar="[NAME=URL]...",
)

# See also s2gos-client/src/s2gos_client/cli/cli.py
REQUEST_FILE_OPTION = typer.Option(
    ...,
    "--request",
    "-r",
    help="Processing request file. Use `-` to read from <stdin>.",
    metavar="PATH",
)
