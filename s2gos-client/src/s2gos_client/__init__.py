#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from importlib.metadata import version

from .api import AsyncClient, Client, ClientConfig, ClientError

__version__ = version("s2gos-client")

__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "ClientError",
    "__version__",
]
