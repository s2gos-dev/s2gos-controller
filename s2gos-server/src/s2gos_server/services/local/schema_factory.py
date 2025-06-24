#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import copy
import datetime
from types import GenericAlias, NoneType, UnionType
from typing import Any, TypeAlias, Union, get_args, get_origin

from pydantic import BaseModel

from s2gos.common.models import Schema

Annotation: TypeAlias = type | GenericAlias | UnionType | NoneType


class SchemaFactory:
    unary_schemas: dict[type, dict[str, Any]] = {
        NoneType: {"nullable": True},
        bool: {"type": "boolean"},
        int: {"type": "integer"},
        float: {"type": "number"},
        str: {"type": "string"},
        tuple: {"type": "array"},
        list: {"type": "array"},
        set: {"type": "array"},
        dict: {"type": "object"},
        datetime.date: {"type": "string", "format": "date"},
        datetime.datetime: {"type": "string", "format": "datetime"},
    }

    def __init__(
        self,
        fn_name: str,
        name: str,
        annotation: Annotation,
        *,
        default: Any = ...,
        is_return: bool = False,
    ):
        self.fn_name = fn_name
        self.name = name
        self.annotation = annotation
        self.default = default
        self.is_return = is_return

    def get_schema(self) -> Schema:
        schema_dict = self.get_schema_dict()
        return Schema.model_validate(schema_dict)

    def get_schema_dict(self) -> dict[str, Any]:
        schema_dict = self._annotation_to_schema_dict(self.annotation)
        if self.default is not ...:
            schema_dict["default"] = _serialize_for_json(self.default)
        return schema_dict

    def _annotation_to_schema_dict(self, annotation: Annotation) -> dict[str, Any]:
        if annotation is Any or annotation is ...:
            return {}
        if annotation is NoneType:
            return {"nullable": True}

        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is None:
            origin = annotation

        # TODO: handle Literal[...]

        if isinstance(origin, UnionType) or origin is UnionType or origin is Union:
            if NoneType in args:
                args = tuple(filter(lambda arg: arg is not NoneType, args))
                if len(args) == 1:
                    return {
                        **self._annotation_to_schema_dict(args[0]),
                        "nullable": True,
                    }
                else:
                    return {
                        "oneOf": [self._annotation_to_schema_dict(arg) for arg in args],
                        "nullable": True,
                    }
            return {"oneOf": [self._annotation_to_schema_dict(arg) for arg in args]}

        if args:
            if origin is tuple:
                return {
                    "type": "array",
                    "items": [self._annotation_to_schema_dict(arg) for arg in args],
                    "minItems": len(args),
                    "maxItems": len(args),
                }
            if origin in (list, set):
                return {
                    "type": "array",
                    "items": self._annotation_to_schema_dict(args[0]),
                }
            if origin is dict:
                return {
                    "type": "object",
                    "additionalProperties": self._annotation_to_schema_dict(args[1]),
                }

        if issubclass(origin, BaseModel):
            schema = origin.model_json_schema(mode="serialization")
            return _sanitize_pydantic_json_schema(schema)

        schema = self.unary_schemas.get(origin)
        if schema is not None:
            return copy.deepcopy(schema) if schema is not None else {}

        if self.is_return:
            item = f"return value {self.name!r}"
        else:
            item = f"parameter {self.name!r}"

        raise ValueError(
            f"Unhandled annotation '{annotation}' for {item} of {self.fn_name!r}"
        )


def _serialize_for_json(value):
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def _sanitize_pydantic_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    pydantic v2.11.4 creates the following schema from an attribute
    declaration `name: Optional[str] = None`:
    ```
        {
            'anyOf': [{'type': 'string'}, {'type': 'null'}],
            'default': None,
            'title': 'Name'
        }
    ```
    We sanitize it into the following, less verbose, OpenAPI 3.0
    compliant version:
    ```
        {
            'type': 'string',
            'nullable': True,
            'default': None,
            'title': 'Name'
        }
    ```
    """
    new_schema = copy.deepcopy(schema)
    _sanitize_pydantic_json_schema_in_place(new_schema)
    return new_schema


def _sanitize_pydantic_json_schema_in_place(schema: dict[str, Any]) -> None:
    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        type_spec = list(any_of)
        try:
            type_spec.remove({"type": "null"})
        except ValueError:
            pass
        if len(type_spec) == 1:
            schema.pop("anyOf")
            schema.update(**type_spec[0], nullable=True)
        # no other schema elements expected if "anyOf" exists
        return
    _sanitize_pydantic_json_schema_container(schema, "properties")
    _sanitize_pydantic_json_schema_container(schema, "additionalProperties")
    _sanitize_pydantic_json_schema_container(schema, "items")
    _sanitize_pydantic_json_schema_container(schema, "additionalItems")


def _sanitize_pydantic_json_schema_container(
    schema: dict[str, Any], property_name: str
) -> None:
    schema_container = schema.get(property_name)
    if isinstance(schema_container, dict):
        for s in list(schema_container.values()):
            _sanitize_pydantic_json_schema_in_place(s)
    elif isinstance(schema_container, list):
        for s in schema_container:
            _sanitize_pydantic_json_schema_in_place(s)
