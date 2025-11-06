#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from cuiman.cli import get_cli

cli = get_cli("s2gos-client")

__all__ = [
    "cli",
]

if __name__ == "__main__":
    cli()
