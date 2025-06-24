#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Literal

from pydantic import BaseModel

from s2gos.client.transport import Transport


class MockTransport(Transport):  # pragma: no cover
    def __init__(self):
        self._call_stack = []

    @property
    def call_stack(self) -> list[dict]:
        return self._call_stack

    def call(
        self,
        path: str,
        method: Literal["get", "post", "put", "delete"],
        path_params: dict[str, Any],
        query_params: dict[str, Any],
        request: BaseModel | None,
        return_types: dict[str, type | None],
        error_types: dict[str, type | None],
    ) -> Any:
        self._call_stack.append(
            dict(
                path=path,
                method=method,
                path_params=path_params,
                query_params=query_params,
                request=request,
                return_types=return_types,
                error_types=error_types,
            )
        )
        return_type = return_types.get("200", return_types.get("201"))
        # noinspection PyTypeChecker
        return object.__new__(return_type) if return_type is not None else None
