#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from importlib.metadata import version

from .client import Client
from .config import ClientConfig
from .exceptions import ClientException

__version__ = version("s2gos-client")

__all__ = ["Client", "ClientConfig", "ClientException", "__version__"]
