#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from collections.abc import Iterator, Mapping
from typing import Callable, Optional

import pydantic

from .process import Process


class ProcessRegistry(Mapping[str, Process]):
    def __init__(self):
        self._processes: dict[str, Process] = {}

    def __getitem__(self, process_id: str, /) -> Process:
        return self._processes[process_id]

    def __len__(self) -> int:
        return len(self._processes)

    def __iter__(self) -> Iterator[str]:
        return iter(self._processes)

    # noinspection PyShadowingBuiltins
    def register(
        self,
        function: Optional[Callable] = None,
        /,
        *,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
        output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
    ) -> Callable[[Callable], Callable] | Callable:
        """
        A decorator that can be applied to a user function in order to
        register it as a process in this registry.

        The decorator can be used with or without parameters.
        """

        def register_process(fn: Callable):
            process = Process.create(
                fn,
                id=id,
                version=version,
                title=title,
                description=description,
                input_fields=input_fields,
                output_fields=output_fields,
            )
            self._processes[process.description.id] = process
            return fn

        if function is not None:
            return register_process(function)
        else:
            return register_process
