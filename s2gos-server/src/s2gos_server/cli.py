#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from wraptile.cli import new_cli

from s2gos_server import __version__ as version

cli = new_cli(name="s2gos-server", version=version)

__all__ = ["cli"]

if __name__ == "__main__":  # pragma: no cover
    cli()
