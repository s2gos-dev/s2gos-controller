#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Callable, Optional

import pydantic

from s2gos_common.models import ProcessDescription
from s2gos_server.services.base.function_process import FunctionProcess


class ProcessRegistry:
    def __init__(self):
        self._processes: dict[str, FunctionProcess] = {}

    def get_process_list(self) -> list[ProcessDescription]:
        return [v.process for v in self._processes.values()]

    def get_process(self, process_id: str) -> Optional[ProcessDescription]:
        entry = self._processes.get(process_id)
        return entry.process if entry is not None else None

    def get_process_entry(self, process_id: str) -> Optional[FunctionProcess]:
        return self._processes.get(process_id)

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
    ) -> FunctionProcess:
        process = FunctionProcess.from_function(
            function,
            id=id,
            version=version,
            title=title,
            description=description,
            input_fields=input_fields,
            output_fields=output_fields,
        )
        self._processes[process.process.id] = process
        return process
