#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from cuiman.cli import new_cli

from s2gos_client import __version__ as version

cli = new_cli(
    name="s2gos-client",
    version=version,
    summary="Interact with the ESA DTE S2GOS processing service.",
)

__all__ = [
    "cli",
]

if __name__ == "__main__":  # pragma: no cover
    cli()
