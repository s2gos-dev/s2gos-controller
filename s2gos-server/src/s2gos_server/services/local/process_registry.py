#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from collections.abc import Iterator, Mapping
from typing import Callable, Optional

import pydantic

from s2gos_server.services.local.registered_process import RegisteredProcess


class ProcessRegistry(Mapping[str, RegisteredProcess]):
    def __init__(self):
        self._processes: dict[str, RegisteredProcess] = {}

    def __getitem__(self, process_id: str, /) -> RegisteredProcess:
        return self._processes[process_id]

    def __len__(self) -> int:
        return len(self._processes)

    def __iter__(self) -> Iterator[str]:
        return iter(self._processes)

    def get_process_entries(self) -> list[RegisteredProcess]:
        return list(self._processes.values())

    # noinspection PyShadowingBuiltins
    def register_function(
        self,
        function: Callable,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
        output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
    ) -> RegisteredProcess:
        process = RegisteredProcess.from_function(
            function,
            id=id,
            version=version,
            title=title,
            description=description,
            input_fields=input_fields,
            output_fields=output_fields,
        )
        self._processes[process.description.id] = process
        return process
