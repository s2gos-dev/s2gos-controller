#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal
from urllib.parse import urljoin

import requests
import uri_template
from pydantic import BaseModel

from s2gos_client.api.exceptions import ClientException


@dataclass
class TransportArgs:
    path: str
    method: Literal["get", "post", "put", "delete"] = "get"
    path_params: dict[str, Any] = field(default_factory=dict)
    query_params: dict[str, Any] = field(default_factory=dict)
    request: BaseModel | None = None
    return_types: dict[str, type | None] = field(default_factory=dict)
    error_types: dict[str, type | None] = field(default_factory=dict)
    extra_kwargs: dict[str, Any] = field(default_factory=dict)

    def get_url(self, server_url: str) -> str:
        return urljoin(server_url, uri_template.expand(self.path, **self.path_params))

    def get_json_for_request(self) -> Any:
        request = self.request
        return (
            request.model_dump(
                mode="json", by_alias=True, exclude_none=True, exclude_defaults=True
            )
            if isinstance(request, BaseModel)
            else request
        )

    def get_response_for_json(self, status_code: int, json_data: Any):
        status_key = str(status_code)
        return_type = self.return_types.get(status_key)
        if (
            return_type is not None
            and inspect.isclass(return_type)
            and issubclass(return_type, BaseModel)
        ):
            return return_type.model_validate(json_data)
        else:
            return json_data

    # noinspection PyMethodMayBeStatic
    def get_error_for_json(
        self, status_code: int, reason: str | None, json_data: Any
    ) -> ClientException:
        kwargs = {}
        if isinstance(json_data, dict):
            kwargs = dict(
                title=json_data.get("title"),
                detail=json_data.get("detail"),
            )
        return ClientException(status_code, reason, **kwargs)


class Transport(ABC):
    """Abstraction of the transport that calls a web API in synchronous mode."""

    @abstractmethod
    def call(self, args: TransportArgs) -> Any:
        """
        Synchronously call a web API with the given endpoint
        `path`, `method`, `params`, etc. Then validate the response
        and return an instance of one of the types given by
        `return_types`.
        """


class AsyncTransport(ABC):
    """Abstraction of the transport that calls a web API in asynchronous mode."""

    @abstractmethod
    async def async_call(self, args: TransportArgs) -> Any:
        """
        Asynchronously call a web API with the given endpoint
        `path`, `method`, `params`, etc. Then validate the response
        and return an instance of one of the types given by
        `return_types`.
        """


class DefaultTransport(Transport, AsyncTransport):
    """A concrete web API transport based on the requests package."""

    def __init__(self, server_url: str, debug: bool = False):
        self.server_url = server_url
        self.debug = debug

    def call(self, args: TransportArgs) -> Any:
        url = args.get_url(self.server_url)
        request_json = args.get_json_for_request()
        response = requests.request(
            args.method.upper(),
            url,
            params=args.query_params,
            json=request_json,
            **args.extra_kwargs,
        )
        response_json = response.json()
        if response.ok:
            return args.get_response_for_json(response.status_code, response_json)
        else:
            raise args.get_error_for_json(
                response.status_code, response.reason, response_json
            )

    def async_call(self, args: TransportArgs) -> Any:
        return self.call(args)
