#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Optional, get_args, get_origin

import pydantic

from s2gos_common.models import (
    InputDescription,
    OutputDescription,
    ProcessDescription,
)

from .schema import create_json_schema, create_schema_instance


@dataclass
class Process:
    """
    A process comprises a process description and executable code
    in form of a Python function.
    """

    function: Callable
    signature: inspect.Signature
    model_class: type[pydantic.BaseModel]
    description: ProcessDescription

    # noinspection PyShadowingBuiltins
    @classmethod
    def create(
        cls,
        function: Callable,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
        output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
    ) -> "Process":
        if not inspect.isfunction(function):
            raise ValueError("function argument must be callable")
        fn_name = f"{function.__module__}:{function.__qualname__}"
        id = id or fn_name
        version = version or "0.0.0"
        description = description or inspect.getdoc(function)
        signature = inspect.signature(function)
        inputs, model_class = _generate_inputs(fn_name, signature, input_fields)
        outputs = _generate_outputs(fn_name, signature.return_annotation, output_fields)
        return Process(
            function=function,
            signature=signature,
            model_class=model_class,
            description=ProcessDescription(
                id=id,
                version=version,
                title=title,
                description=description,
                inputs=inputs,
                outputs=outputs,
                # Note, we may later add the following:
                # metadata=metadata,
                # keywords=keywords,
                # links=links,
                # outputTransmission=output_transmission,
                # jobControlOptions=job_control_options,
            ),
        )


def _generate_inputs(
    fn_name: str,
    signature: inspect.Signature,
    input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] | None,
) -> tuple[dict[str, InputDescription], type[pydantic.BaseModel]]:
    model_field_definitions = {}
    for param_name, parameter in signature.parameters.items():
        if parameter.default is inspect.Parameter.empty:
            field = parameter.annotation
        else:
            field = parameter.annotation, parameter.default
        model_field_definitions[param_name] = field
    model_class = pydantic.create_model("Inputs", **model_field_definitions)
    if input_fields:
        invalid_inputs = [
            input_name
            for input_name in input_fields
            if input_name not in signature.parameters
        ]
        if invalid_inputs:
            raise ValueError(
                f"function {fn_name!r}: "
                "all input names must have corresponding parameter names; "
                f"invalid input name(s): {', '.join(map(repr, invalid_inputs))}"
            )
        # noinspection PyTypeChecker
        model_field_definitions = dict(model_class.model_fields)
        for input_name, field_info in input_fields.items():
            if input_name in model_field_definitions:
                old_field_info = model_field_definitions[input_name]
                parameter = signature.parameters[input_name]
                model_field_definitions[input_name] = (
                    parameter.annotation,
                    pydantic.fields.FieldInfo.merge_field_infos(
                        old_field_info, field_info
                    ),
                )
        model_class = pydantic.create_model("Inputs", **model_field_definitions)
    inputs_schema = create_json_schema(model_class)

    input_descriptions = {}
    for input_name, schema in inputs_schema.get("properties", {}).items():
        input_descriptions[input_name] = InputDescription(
            minOccurs=1 if input_name in inputs_schema.get("required", []) else 0,
            maxOccurs=None,
            title=schema.pop("title", None),
            description=schema.pop("description", None),
            schema=create_schema_instance(input_name, schema),
        )

    return input_descriptions, model_class


def _generate_outputs(
    fn_name: str,
    annotation: type,
    output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] | None,
) -> dict[str, OutputDescription]:
    model_field_definitions: dict[str, Any] = {}
    if not output_fields:
        model_field_definitions = {"return_value": annotation}
    elif len(output_fields) == 1:
        output_name, field_info = next(iter(output_fields.items()))
        model_field_definitions = {output_name: (annotation, field_info)}
    else:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if not (origin is tuple and args):
            raise TypeError(
                f"function {fn_name!r}: return type must be tuple[] with arguments"
            )
        if len(args) != len(output_fields):
            raise ValueError(
                f"function {fn_name!r}: number of outputs must match number "
                f"of tuple[] arguments"
            )
        for arg_type, (output_name, field_info) in zip(args, output_fields.items()):
            model_field_definitions[output_name] = (arg_type, field_info)
    model_class = pydantic.create_model("Outputs", **model_field_definitions)
    outputs_schema = create_json_schema(model_class)
    output_descriptions = {}
    for output_name, schema in outputs_schema.get("properties", {}).items():
        output_descriptions[output_name] = OutputDescription(
            title=schema.pop("title", None),
            description=schema.pop("description", None),
            schema=create_schema_instance(output_name, schema),
        )
    return output_descriptions


def _get_qual_name(function: Callable) -> str:
    # noinspection PyUnresolvedReferences
    return f"{function.__module__}:{function.__qualname__}"
