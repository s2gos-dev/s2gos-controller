#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import ABC
from typing import Optional

import fastapi
from starlette.routing import Route

from s2gos_common.models import (
    Capabilities,
    ConformanceDeclaration,
    Link,
)
from s2gos_common.service import Service

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
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        conforms_to: Optional[list[str]] = None,
    ):
        self.title = title
        self.description = description
        self.conforms_to = conforms_to or DEFAULT_CONFORMS_TO

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
