#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import json
from collections.abc import Iterator, Mapping
from typing import Callable, Optional, Any

import pydantic

from .registered_process import RegisteredProcess


class ProcessRegistry(Mapping[str, RegisteredProcess]):
    def __init__(self):
        self._processes: dict[str, RegisteredProcess] = {}

    def __getitem__(self, process_id: str, /) -> RegisteredProcess:
        return self._processes[process_id]

    def __len__(self) -> int:
        return len(self._processes)

    def __iter__(self) -> Iterator[str]:
        return iter(self._processes)

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

    def to_json_dict(self, use_qual_names: bool = False) -> dict[str, Any]:
        """Convert this registry into a JSON-serializable dictionary"""
        return {
            (v.qual_name if use_qual_names else k): v.description.model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True,
                exclude_defaults=True,
                exclude_unset=True,
            )
            for k, v in self.items()
        }

    def to_json(self, use_qual_names: bool = False, **kwargs) -> str:
        return json.dumps(self.to_json_dict(use_qual_names=use_qual_names), **kwargs)
