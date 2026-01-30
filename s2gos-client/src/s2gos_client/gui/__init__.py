#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from importlib import import_module

from cuiman.gui import Client
from .pathref import register_component


# Setup S2GOS-specific API configuration
import_module("s2gos_client.api")

register_component()

__all__ = [
    "Client",
]
