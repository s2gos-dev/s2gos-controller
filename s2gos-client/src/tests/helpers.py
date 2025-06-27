#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any

from s2gos_client.api.transport import Transport, TransportArgs


class MockTransport(Transport):  # pragma: no cover
    def __init__(self):
        self._call_stack = []

    @property
    def call_stack(self) -> list[dict]:
        return self._call_stack

    def call(self, args: TransportArgs) -> Any:
        self._call_stack.append(
            dict(
                path=args.path,
                method=args.method,
                path_params=args.path_params,
                query_params=args.query_params,
                request=args.request,
                return_types=args.return_types,
                error_types=args.error_types,
            )
        )
        return_type = args.return_types.get("200", args.return_types.get("201"))
        # noinspection PyTypeChecker
        return object.__new__(return_type) if return_type is not None else None
