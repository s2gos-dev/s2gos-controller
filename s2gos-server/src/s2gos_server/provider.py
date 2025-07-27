#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import ast
import importlib
import logging
import os
import shlex

from s2gos_common.service import Service

from .constants import S2GOS_SERVICE_ENV_VAR, S2GOS_SERVICE_ARGS_ENV_VAR
from .services.base import ServiceBase


def get_service() -> Service:
    return ServiceProvider.get_instance()


class ServiceProvider:
    _service: Service | None = None

    @classmethod
    def get_instance(cls) -> Service:
        if cls._service is None:
            cls.set_instance(cls._load_service())
        assert cls._service is not None
        return cls._service

    @classmethod
    def set_instance(cls, service: Service):
        cls._service = service
        logger = logging.getLogger("uvicorn")
        logger.info(f"Using service instance of type {type(service).__name__}")

    @classmethod
    def _load_service(cls) -> Service:
        service_ref: str | None = os.environ.get(S2GOS_SERVICE_ENV_VAR)
        if not service_ref:
            raise RuntimeError(
                "Service not specified. "
                f"Please set environment variable {S2GOS_SERVICE_ENV_VAR!r}."
            )
        module_name, class_name = service_ref.split(":", maxsplit=1)
        module = importlib.import_module(module_name)
        service: Service = getattr(module, class_name)
        if not isinstance(service, Service):
            raise TypeError("{service_ref!r} is not a service")
        if isinstance(service, ServiceBase):
            service_args_value: str | None = os.environ.get(S2GOS_SERVICE_ARGS_ENV_VAR)
            if service_args_value:
                service_args = shlex.split(service_args_value)
                args = []
                kwargs = {}
                for a in service_args:
                    if a.startswith("-"):
                        if not a.startswith("--"):
                            raise ValueError(f"Unexpected option: {a}")
                        kv = [p.strip() for p in a[2:].split("=", maxsplit=1)]
                        if len(kv) == 1:
                            kwargs[kv[0]] = True
                        else:
                            kwargs[kv[0]] = ast.literal_eval(kv[1])
                    else:
                        args.append(a)
                if service_args:
                    service.configure(*args, **kwargs)
        return service
