#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any

from s2gos_client.api.transport import AsyncTransport, Transport, TransportArgs


class MockTransport(AsyncTransport, Transport):  # pragma: no cover
    def __init__(self):
        self.calls: list[TransportArgs] = []
        self.async_calls: list[TransportArgs] = []
        self.closed = False

    def call(self, args: TransportArgs) -> Any:
        self.calls.append(args)
        return self._create_model_object(args)

    async def async_call(self, args: TransportArgs) -> Any:
        self.async_calls.append(args)
        return self._create_model_object(args)

    @staticmethod
    def _create_model_object(args: TransportArgs) -> Any:
        return_type = args.return_types.get("200", args.return_types.get("201"))
        # noinspection PyTypeChecker
        return object.__new__(return_type) if return_type is not None else None

    def close(self):
        self.closed = True

    async def async_close(self):
        self.closed = True
