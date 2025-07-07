#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import copy
import dataclasses
import inspect
import json
from typing import Any, Callable, Optional, get_args, get_origin

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

    # noinspection PyShadowingBuiltins
    def register_function(
        self,
        function: Callable,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        inline_inputs: bool | str | list[str] = False,
        inline_sep: str | None = ".",
        input_fields: dict[str, pydantic.fields.FieldInfo] = None,
        output_fields: dict[str, pydantic.fields.FieldInfo] = None,
    ) -> "ProcessRegistry.Entry":
        if not inspect.isfunction(function):
            raise ValueError("function argument must be callable")
        fn_name = f"{function.__module__}:{function.__qualname__}"
        id = id or fn_name
        version = version or "0.0.0"
        description = description or inspect.getdoc(function)
        signature = inspect.signature(function)
        inputs = _generate_inputs(
            fn_name, signature, input_fields, inline_inputs, inline_sep
        )
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
    input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] | None,
    inline_inputs: bool | str | list[str],
    inline_sep: str | None,
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
        model_class: type[pydantic.BaseModel] = pydantic.create_model(
            "Inputs", **model_field_definitions
        )
    inputs_schema = create_json_schema(
        model_class, inline_objects=inline_inputs, inline_sep=inline_sep
    )

    input_descriptions = {}
    for input_name, schema in inputs_schema.get("properties", {}).items():
        input_descriptions[input_name] = InputDescription(
            minOccurs=1 if input_name in inputs_schema.get("required", []) else 0,
            maxOccurs=None,
            title=schema.pop("title", None),
            description=schema.pop("description", None),
            schema=create_schema_instance(input_name, schema),
        )
    return input_descriptions


def _generate_outputs(
    fn_name: str,
    annotation: type,
    output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] | None,
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
    inline_objects: bool | str | list[str] = False,
    inline_sep: str | None = ".",
) -> dict[str, Any]:
    schema = model_class.model_json_schema(mode="serialization")
    schema = inline_schema_refs(schema)
    if inline_objects and isinstance(schema.get("properties"), dict):
        schema = inline_object_properties(schema, inline_objects, inline_sep)
    return backport_schema_to_openapi_3_0(schema)


def inline_object_properties(
    schema: dict[str, Any],
    inline_objects: bool | str | list[str],
    inline_sep: str | None,
):
    if isinstance(inline_objects, str):
        inline_names = {inline_objects}
    elif isinstance(inline_objects, list):
        inline_names = set(inline_objects)
    else:
        inline_names = set()
    obj_keys_to_be_inlined = [
        obj_key
        for obj_key, obj_schema in schema["properties"].items()
        if obj_schema.get("type") == "object"
        and isinstance(obj_schema.get("properties"), dict)
        and (inline_objects is True or obj_key in inline_names)
    ]
    if obj_keys_to_be_inlined:
        schema_properties: dict[str, Any] = dict(schema["properties"])
        schema_required: list[str] = list(schema.get("required", []))
        for obj_key in obj_keys_to_be_inlined:
            obj_schema: dict[str, Any] = schema_properties.pop(obj_key)
            properties = obj_schema.get("properties")
            required = obj_schema.get("required", [])
            new_properties: dict[str, Any] = {}
            new_required: list[str] = []
            for k2, s2 in properties.items():
                new_key = f"{obj_key}{inline_sep}{k2}" if inline_sep else k2
                new_properties[new_key] = s2
                if k2 in required:
                    new_required.append(new_key)
            schema_properties.update(new_properties)
            schema_required = list({*schema_required, *new_required})
        schema: dict[str, Any] = dict(schema)
        schema["properties"] = schema_properties
        schema["required"] = schema_required
    return schema


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
