#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from wraptile.cli import get_cli

from s2gos_server import __version__ as version

cli = get_cli("s2gos-server", version=version)

__all__ = ["cli"]

if __name__ == "__main__":  # pragma: no cover
    cli()
