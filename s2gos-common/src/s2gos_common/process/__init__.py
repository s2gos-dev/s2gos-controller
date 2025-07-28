#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from .process_registry import ProcessRegistry
from .registered_process import RegisteredProcess

__all__ = [
    "ProcessRegistry",
    "RegisteredProcess",
]
