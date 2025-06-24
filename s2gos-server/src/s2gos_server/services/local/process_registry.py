#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import dataclasses
import inspect
from typing import (
    Any,
    Callable,
    Optional,
    get_args,
    get_origin,
)

from s2gos.common.models import (
    InputDescription,
    OutputDescription,
    ProcessDescription,
    Schema,
)
from s2gos.server.services.local.schema_factory import Annotation, SchemaFactory


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
        self, function: Callable, **kwargs
    ) -> "ProcessRegistry.Entry":
        if not inspect.isfunction(function):
            raise ValueError("function argument must be callable")

        fn_name = f"{function.__module__}:{function.__qualname__}"

        id_ = kwargs.pop("id", None) or fn_name
        version = kwargs.pop("version", None) or "0.0.0"
        input_schemas = kwargs.pop("inputs", None) or {}
        output_schemas = kwargs.pop("outputs", None) or {}
        description = kwargs.pop("description", None) or function.__doc__

        signature = inspect.signature(function)
        if not input_schemas:
            inputs = _generate_inputs(fn_name, signature)
        else:
            inputs = _complete_inputs(fn_name, signature, input_schemas)

        if not output_schemas:
            outputs = _generate_outputs(fn_name, signature.return_annotation)
        else:
            outputs = _complete_outputs(fn_name, signature, output_schemas)

        entry = ProcessRegistry.Entry(
            function,
            signature,
            ProcessDescription(
                id=id_,
                version=version,
                description=description,
                inputs=inputs,
                outputs=outputs,
                **kwargs,
            ),
        )
        self._dict[id_] = entry
        return entry


def _generate_inputs(
    fn_name: str, signature: inspect.Signature
) -> dict[str, InputDescription]:
    return {
        param_name: _generate_input(fn_name, param)
        for param_name, param in signature.parameters.items()
        if param_name != "ctx"
    }


def _complete_inputs(
    fn_name: str, signature: inspect.Signature, input_schemas: dict[str, Any]
):
    assert isinstance(input_schemas, dict)

    unknown_input_names = [
        k for k in input_schemas.keys() if k not in signature.parameters
    ]
    if unknown_input_names:
        raise ValueError(f"Invalid input name(s): {', '.join(unknown_input_names)}")

    _inputs: dict[str, InputDescription] = {}
    for param_name, parameter in signature.parameters.items():
        if param_name not in input_schemas:
            _inputs[param_name] = _generate_input(fn_name, parameter)
        else:
            input_schema_dict = input_schemas[param_name]
            assert isinstance(input_schema_dict, dict)

            schema_factory = _schema_factory_from_parameter(fn_name, parameter)
            param_schema_dict = schema_factory.get_schema_dict()

            merged_schema_dict = dict(param_schema_dict)
            merged_schema_dict.update(input_schema_dict)

            merged_schema = Schema.model_validate(merged_schema_dict)

            _inputs[param_name] = InputDescription(schema=merged_schema)

    return _inputs


def _generate_input(fn_name: str, parameter: inspect.Parameter) -> InputDescription:
    schema_factory = _schema_factory_from_parameter(fn_name, parameter)
    return InputDescription(schema=schema_factory.get_schema())


def _generate_outputs(
    fn_name: str, annotation: Annotation
) -> dict[str, OutputDescription]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is tuple and args:
        return {
            f"result_{i}": _generate_output(fn_name, f"result_{i}", arg)
            for i, arg in enumerate(args)
        }
    else:
        return {"result": _generate_output(fn_name, "result", annotation)}


def _complete_outputs(
    _fn_name: str,
    _signature: inspect.Signature,
    output_schemas: dict[str, OutputDescription],
):
    assert isinstance(output_schemas, dict)
    # TODO: implement _complete_outputs()
    return dict(output_schemas)


def _generate_output(
    fn_name: str, name: str, annotation: Annotation
) -> OutputDescription:
    return OutputDescription(
        schema=_schema_from_return_annotation(fn_name, name, annotation)
    )


def _schema_factory_from_parameter(
    fn_name: str, parameter: inspect.Parameter
) -> SchemaFactory:
    return SchemaFactory(
        fn_name,
        parameter.name,
        _normalize_inspect_value(parameter.annotation, default=Any),
        default=_normalize_inspect_value(parameter.default, default=...),
    )


def _schema_from_parameter(fn_name: str, parameter: inspect.Parameter) -> Schema:
    return SchemaFactory(
        fn_name,
        parameter.name,
        _normalize_inspect_value(parameter.annotation, default=Any),
        default=_normalize_inspect_value(parameter.default, default=...),
    ).get_schema()


def _schema_from_return_annotation(
    fn_name: str,
    name: str,
    annotation: Annotation,
) -> Schema:
    return SchemaFactory(
        fn_name,
        name,
        _normalize_inspect_value(annotation, default=Any),
        is_return=True,
    ).get_schema()


def _normalize_inspect_value(value: Any, *, default: Any) -> Any:
    if value is inspect.Parameter.empty:
        return default
    return value
