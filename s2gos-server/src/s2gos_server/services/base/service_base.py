#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import importlib
import logging
import os
import shlex
from abc import ABC
from typing import Optional

import fastapi
import yaml
from starlette.routing import Route

from s2gos_common.models import (
    Capabilities,
    ConformanceDeclaration,
    Link,
)
from s2gos_common.service import Service
from s2gos_server.constants import ENV_VAR_SERVICE
from s2gos_server.exceptions import ConfigException

DEFAULT_CONFORMS_TO = [
    "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
    "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/ogc-process-description",
    "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json",
    # "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/html",
    "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30",
    "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
    # "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/callback",
    "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/dismiss",
]


class ServiceBase(Service, ABC):
    @classmethod
    def load(cls) -> "ServiceBase":
        """
        Load the service instance from environment variable.

        Returns:
            A configured service instance of type `ServiceBase`.

        Raises:
            ConfigException: if a server configuration error occurs.
        """
        service_spec: str | None = os.environ.get(ENV_VAR_SERVICE)
        service_args = shlex.split(service_spec) if service_spec else []
        args = []
        kwargs = {}
        for a in service_args:
            if a.startswith("-"):
                if not a.startswith("--"):
                    kv_example = "--key[=value]"
                    raise ConfigException(
                        f"Service options must have the form {kv_example!r}, "
                        f"but got {a!r}."
                    )
                kv = [p.strip() for p in a[2:].split("=", maxsplit=1)]
                k = kv[0]
                k = k.replace("-", "_")
                maybe_invert = k.startswith("no_") and len(k) > 3
                if not k.isidentifier():
                    kv_example = "--key[=value]"
                    raise ConfigException(
                        f"Service options must have the form {kv_example!r}, "
                        f"but got {kv[0]!r} as key, which is not an identifier."
                    )
                v = yaml.safe_load(kv[1]) if len(kv) == 2 else True
                if maybe_invert and isinstance(v, bool):
                    kwargs[k[3:]] = not v
                else:
                    kwargs[k] = v
            else:
                args.append(a)

        service_name_example = "path.to.module:service"
        if not args:
            service_help = (
                f"The service must be passed in the form {service_name_example!r} "
                "either as first command-line argument or using the environment "
                f"variable {ENV_VAR_SERVICE!r}."
            )
            raise ConfigException(f"Service not specified. {service_help}")

        service_name, args = args[0], args[1:]
        try:
            module_name, attr_name = service_name.split(":", maxsplit=1)
        except ValueError:
            raise ConfigException(
                f"The service must be passed in the form {service_name_example!r}, "
                f"but got {service_name!r}."
            )
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            raise ConfigException(f"Cannot import the service module {module_name!r}.")
        try:
            service: Service = getattr(module, attr_name)
        except AttributeError:
            raise ConfigException(
                f"Service module {module_name!r} has no attribute {attr_name!r}."
            )
        if not isinstance(service, ServiceBase):
            raise ConfigException(
                f"{service_name!r} is not referring to a service instance."
            )
        logger = logging.getLogger("uvicorn")
        logger.info(f"Created service instance of type {type(service).__name__}")
        service.configure(*args, **kwargs)
        return service

    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        conforms_to: Optional[list[str]] = None,
    ):
        self.title = title
        self.description = description
        self.conforms_to = conforms_to or DEFAULT_CONFORMS_TO
        self.logger = logging.getLogger("uvicorn")

    # noinspection PyMethodMayBeStatic
    def configure(self, *args, **kwargs):
        """Configure this service by the given positional and keyword arguments.

        The default implementation does nothing.

        Args:
            args: positional arguments.
            kwargs: keyword arguments.

        Raises:
            ConfigException: if a server configuration error occurs.
        """

    async def get_capabilities(
        self, request: fastapi.Request, **kwargs
    ) -> Capabilities:
        app: fastapi.FastAPI = request.app
        links = [self.get_self_link(request, "get_capabilities")] + [
            Link(
                href=self.get_url(request, r.path),
                title=r.name,
                rel="service",
                type=self.get_link_type(r.name),
                hreflang="en",
            )
            for r in app.routes
            if isinstance(r, Route)
        ]
        return Capabilities(
            title=self.title,
            description=self.description,
            links=links,
        )

    async def get_conformance(self, **_kwargs) -> ConformanceDeclaration:
        return ConformanceDeclaration(conformsTo=self.conforms_to)

    @classmethod
    def get_self_link(cls, request: fastapi.Request, name: str, **path_params) -> Link:
        return Link(
            href=str(request.url_for(name, **path_params)),
            rel="self",
            title=name,
            type=cls.get_link_type(name),
            hreflang="en",
        )

    @classmethod
    def get_link_type(cls, name: str) -> str:
        html_names = ("swagger_ui_html", "swagger_ui_redirect", "redoc_html")
        return "text/html" if name in html_names else "application/json"

    @classmethod
    def get_url(cls, request: fastapi.Request, path: str):
        return str(request.base_url.replace(path=path))
