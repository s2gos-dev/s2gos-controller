#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any
import requests
from .args import TransportArgs
from .transport import AsyncTransport, Transport


class RequestsTransport(Transport, AsyncTransport):
    """A concrete web API transport based on the requests package."""

    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session: requests.Session | None = None

    def call(self, args: TransportArgs) -> Any:
        if self.session is None:
            self.session = requests.Session()
        url = args.get_url(self.server_url)
        request_json = args.get_json_for_request()
        response = self.session.request(
            args.method.upper(),
            url,
            params=args.query_params,
            json=request_json,
            **args.extra_kwargs,
        )
        # TODO: we should only do `response.json()` if JSON is expected,
        #   use args.return_types for this decision.
        response_json = response.json()
        try:
            response.raise_for_status()
            return args.get_response_for_json(response.status_code, response_json)
        except requests.HTTPError as e:
            raise args.get_error_for_json(
                response.status_code, f"{e}", response_json
            ) from e

    async def async_call(self, args: TransportArgs) -> Any:
        return self.call(args)

    def close(self):
        if self.session is not None:
            self.session.close()
            self.session = None

    async def async_close(self):
        self.close()
