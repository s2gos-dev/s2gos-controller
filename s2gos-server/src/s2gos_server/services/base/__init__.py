#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from .function_process import FunctionProcess
from .service_base import DEFAULT_CONFORMS_TO, ServiceBase

__all__ = [
    "FunctionProcess",
    "ServiceBase",
    "DEFAULT_CONFORMS_TO",
]
