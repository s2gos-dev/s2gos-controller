#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import dataclasses
import inspect
from typing import Callable, Optional, get_args, get_origin

import pydantic

from s2gos_common.models import (
    InputDescription,
    OutputDescription,
    ProcessDescription,
    Schema,
)


class ProcessRegistry:
    @dataclasses.dataclass
    class Entry:
        function: Callable
        signature: inspect.Signature
        process: ProcessDescription

    def __init__(self):
        self._dict: dict[str, ProcessRegistry.Entry] = {}

    def get_process_list(self) -> list[ProcessDescription]:
        return [v.process for v in self._dict.values()]

    def get_process(self, process_id: str) -> Optional[ProcessDescription]:
        entry = self._dict.get(process_id)
        return entry.process if entry is not None else None

    def get_entry(self, process_id: str) -> Optional["ProcessRegistry.Entry"]:
        return self._dict.get(process_id)

    def register_function(
        self,
        function: Callable,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        expand_inputs: bool | list[str] = False,
        expand_with_prefix: bool = False,
        input_fields: dict[str, pydantic.fields.FieldInfo] = None,
        output_fields: dict[str, pydantic.fields.FieldInfo] = None,
    ) -> "ProcessRegistry.Entry":
        if not inspect.isfunction(function):
            raise ValueError("function argument must be callable")
        fn_name = f"{function.__module__}:{function.__qualname__}"
        signature = inspect.signature(function)
        inputs = _generate_inputs(fn_name, signature, input_fields)
        outputs = _generate_outputs(fn_name, signature.return_annotation, output_fields)
        entry = ProcessRegistry.Entry(
            function,
            signature,
            ProcessDescription(
                id=id,
                version=version,
                title=title,
                description=description,
                inputs=inputs,
                outputs=outputs,
            ),
        )
        self._dict[id] = entry
        return entry


def _generate_inputs(
    fn_name: str,
    signature: inspect.Signature,
    input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
) -> dict[str, InputDescription]:
    model_field_definitions = {}
    for param_name, parameter in signature.parameters.items():
        if parameter.default is inspect.Parameter.empty:
            field = parameter.annotation
        else:
            field = parameter.annotation, parameter.default
        model_field_definitions[param_name] = field
    model_class = pydantic.create_model("Inputs", **model_field_definitions)
    if input_fields:
        # TODO: check input names match param names
        model_fields: dict[str, pydantic.fields.FieldInfo] = dict(
            model_class.model_fields()
        )
        for input_name, field_info in input_fields.items():
            if input_name in model_fields:
                model_fields[input_name] = pydantic.fields.FieldInfo.merge_field_infos(
                    model_fields[input_name], field_info
                )
        model_class: type[pydantic.BaseModel] = pydantic.create_model(
            "Inputs", **model_field_definitions
        )
    inputs_schema = model_class.model_json_schema(mode="serialization")
    # TODO: 1. respect expanding params
    # TODO: 2. backport schema to OpenAPI 3.0
    return {
        input_name: InputDescription(
            minOccurs=1 if input_name in inputs_schema.get("required", []) else 0,
            maxOccurs=None,
            title=schema.get("title"),
            description=schema.get("description"),
            schema_=Schema(**schema),
        )
        for input_name, schema in inputs_schema["properties"]
    }


def _generate_outputs(
    fn_name: str,
    annotation: type,
    output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
) -> dict[str, OutputDescription]:
    model_field_definitions = {}
    if not output_fields:
        model_field_definitions = {"return_value": annotation}
    elif len(output_fields) == 1:
        output_name, field_info = next(iter(output_fields.items()))
        model_field_definitions = {output_name: (annotation, field_info)}
    else:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if not (origin is tuple and args):
            raise TypeError("return type must be tuple[] with arguments")
        if len(args) != len(output_fields):
            raise TypeError("number of outputs must match number of tuple[] arguments")
        for arg_type, output_name, field_info in zip(args, output_fields):
            model_field_definitions[output_name] = (arg_type, field_info)
    model_class = pydantic.create_model("Outputs", **model_field_definitions)
    outputs_schema = model_class.model_json_schema(mode="serialization")
    return {
        output_name: OutputDescription(
            title=schema.get("title"),
            description=schema.get("description"),
            schema_=Schema(**schema),
        )
        for output_name, schema in outputs_schema["properties"]
    }
