#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import copy
import inspect
import json
from dataclasses import dataclass
from typing import Any, Callable, Optional, get_args, get_origin

import pydantic

from s2gos_common.models import (
    InputDescription,
    OutputDescription,
    ProcessDescription,
    Schema,
)


@dataclass
class RegisteredProcess:
    function: Callable
    signature: inspect.Signature
    description: ProcessDescription
    model_class: type[pydantic.BaseModel]

    # noinspection PyShadowingBuiltins
    @classmethod
    def from_function(
        cls,
        function: Callable,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
        output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
    ) -> "RegisteredProcess":
        if not inspect.isfunction(function):
            raise ValueError("function argument must be callable")
        fn_name = f"{function.__module__}:{function.__qualname__}"
        id = id or function.__name__
        version = version or "0.0.0"
        description = description or inspect.getdoc(function)
        signature = inspect.signature(function)
        inputs, model_class = _generate_inputs(fn_name, signature, input_fields)
        outputs = _generate_outputs(fn_name, signature.return_annotation, output_fields)
        return RegisteredProcess(
            function=function,
            signature=signature,
            description=ProcessDescription(
                id=id,
                version=version,
                title=title,
                description=description,
                inputs=inputs,
                outputs=outputs,
            ),
            model_class=model_class,
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
                f"function {fn_name}: "
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


def create_schema_instance(name: str, schema: dict[str, Any]) -> Schema:
    try:
        return Schema(**schema)
    except pydantic.ValidationError:
        print(80 * ">")
        print("name:", name)
        print("schema:", json.dumps(schema, indent=2))
        print(80 * "<")
        raise


def create_json_schema(
    model_class: type[pydantic.BaseModel],
) -> dict[str, Any]:
    schema = model_class.model_json_schema(mode="serialization")
    schema = inline_schema_refs(schema)
    return backport_schema_to_openapi_3_0(schema)


def inline_schema_refs(schema: dict[str, Any]):
    defs: dict[str, Any] | None = schema.get("$defs")
    if not defs:
        return schema
    schema = copy.copy(schema)
    schema.pop("$defs")
    return _inline_schema_refs(schema, {f"#/$defs/{k}": v for k, v in defs.items()})


def _inline_schema_refs(schema: dict[str, Any], defs: dict[str, Any]):
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in defs:
            ref_schema = _inline_schema_refs(defs[ref], defs)
            schema = copy.copy(schema)
            schema.pop("$ref")
            schema.update(copy.deepcopy(ref_schema))
            return schema
    schema = copy.copy(schema)
    for k in ("allOf", "anyOf", "oneOf"):
        if k in schema:
            if isinstance(schema[k], list):
                schema[k] = [_inline_schema_refs(s, defs) for s in schema[k]]
    for k in ("items", "prefixItems", "additionalProperties"):
        if k in schema:
            if isinstance(schema[k], list):
                schema[k] = [_inline_schema_refs(s, defs) for s in schema[k]]
            else:
                schema[k] = _inline_schema_refs(schema[k], defs)
    for k in ("properties",):
        if k in schema:
            if isinstance(schema[k], dict):
                schema[k] = {
                    k: _inline_schema_refs(s, defs) for k, s in schema[k].items()
                }
    return schema


def backport_schema_to_openapi_3_0(schema: dict[str, Any]):
    if "type" in schema:
        type_ = schema["type"]
        if type_ == "null":
            schema.pop("type")
            schema["nullable"] = True
    if "prefixItems" in schema:
        prefix_items = schema.pop("prefixItems")
        if prefix_items:
            # Care, this is a naive implementation:
            schema["items"] = backport_schema_to_openapi_3_0(prefix_items[0])
    for schema_key in ("items", "additionalProperties"):
        if schema_key in schema:
            if isinstance(schema[schema_key], (list, tuple)):
                schema[schema_key] = list(
                    map(backport_schema_to_openapi_3_0, schema[schema_key])
                )
            elif isinstance(schema[schema_key], dict):
                schema[schema_key] = backport_schema_to_openapi_3_0(schema[schema_key])
    for dict_key in ("properties", "$defs"):
        if dict_key in schema and isinstance(schema[dict_key], dict):
            schema[dict_key] = {
                k: backport_schema_to_openapi_3_0(v)
                for k, v in schema[dict_key].items()
            }
    for x_of_key in ("allOf", "anyOf", "oneOf"):
        if x_of_key in schema:
            schema[x_of_key] = list(
                map(backport_schema_to_openapi_3_0, schema[x_of_key])
            )
            if len(schema[x_of_key]) == 2:
                x_of_copy = [s for s in schema[x_of_key] if s != {"nullable": True}]
                if len(x_of_copy) == 1:
                    schema.pop(x_of_key)
                    schema.update(x_of_copy[0])
                    schema["nullable"] = True
    return schema
