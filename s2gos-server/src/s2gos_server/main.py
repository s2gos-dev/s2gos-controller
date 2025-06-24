#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import importlib
import os

from . import routes
from .app import app
from .constants import S2GOS_SERVICE_ENV_VAR
from .provider import ServiceProvider


def get_service():
    service_impl_spec = os.environ.get(S2GOS_SERVICE_ENV_VAR)
    if not service_impl_spec:
        raise RuntimeError(
            "Error: Service not specified. "
            f"Please set environment variable {S2GOS_SERVICE_ENV_VAR!r}."
        )
    module_name, class_name = service_impl_spec.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    service = getattr(module, class_name)
    print(f"Running service {service}")
    return service


ServiceProvider.set_instance(get_service())

__all__ = ["app", "routes"]
