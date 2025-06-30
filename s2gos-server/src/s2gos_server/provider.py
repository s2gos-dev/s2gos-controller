#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import importlib
import os

from s2gos_common.service import Service

from .constants import S2GOS_SERVICE_ENV_VAR


def get_service() -> Service:
    return ServiceProvider.get_instance()


class ServiceProvider:
    _service: Service | None = None

    @classmethod
    def get_instance(cls) -> Service:
        if cls._service is None:
            cls._service = cls._load_service()
        return cls._service

    @classmethod
    def set_instance(cls, service: Service):
        cls._service = service

    @classmethod
    def _load_service(cls) -> Service:
        service_impl_spec = os.environ.get(S2GOS_SERVICE_ENV_VAR)
        if not service_impl_spec:
            raise RuntimeError(
                "Service not specified. "
                f"Please set environment variable {S2GOS_SERVICE_ENV_VAR!r}."
            )
        module_name, class_name = service_impl_spec.split(":", maxsplit=1)
        module = importlib.import_module(module_name)
        service = getattr(module, class_name)
        return service
