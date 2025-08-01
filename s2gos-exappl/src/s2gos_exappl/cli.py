#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from s2gos_common.process.cli.cli import get_cli


# By using a getter function, we defer importing the registry
# until needed. This avoids early loading of all dependencies
# in the case where the CLI is invoked just with a`--help` option.
def get_process_registry():
    from s2gos_exappl.processes import registry

    return registry


# The CLI with a basic set of commands.
# The `cli` is a Typer application of type `typer.Typer()`,
# so can use the instance to register your own commands.
cli = get_cli(get_process_registry)


__all__ = ["cli"]
