#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from s2gos_common.cli.cli import get_cli


def get_process_registry():
    """This function defers importing the processors package
    until it is required by the CLI. This way no heavy
    package are needed when the CLI is used with `--help` only.
    """
    from s2gos_exappl.processors import registry

    return registry


# The CLI with a basic set of commands.
# You can use the instance to register your own commands.
cli = get_cli(get_process_registry)


__all__ = ["cli"]
