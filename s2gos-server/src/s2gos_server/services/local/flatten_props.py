#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from collections import defaultdict
from collections.abc import Sequence
from typing import Any


def flatten_1st_level_schema_properties(
    schema: dict[str, Any],
    property_names: str | Sequence[str],
):
    flatten_names = normalize_name_set(property_names)
    property_names_to_be_flattened = [
        property_name
        for property_name, property_schema in schema["properties"].items()
        if property_schema.get("type") == "object"
        and isinstance(property_schema.get("properties"), dict)
        and property_name in flatten_names
    ]
    if not property_names_to_be_flattened:
        return schema
    new_properties: dict[str, Any] = dict(schema["properties"])
    new_required: set[str] = set(schema["required"] or [])
    for property_name in property_names_to_be_flattened:
        property_schema: dict[str, Any] = new_properties.pop(property_name)
        properties = property_schema.get("properties") or {}
        required = property_schema.get("required") or []
        for inner_property_name, inner_schema in properties.items():
            new_property_name = f"{property_name}.{inner_property_name}"
            new_properties[new_property_name] = inner_schema
            if inner_property_name in required:
                new_required.add(new_property_name)
    new_schema = dict(schema)
    new_schema["properties"] = new_properties
    new_schema["required"] = sorted(set(r for r in new_required if r in new_properties))
    return new_schema


def unflatten_1st_level_dict_properties(
    mapping: dict[str, Any],
    property_names: str | Sequence[str],
):
    flattened_property_names = normalize_name_set(property_names)
    if not flattened_property_names:
        return mapping
    flattened_mappings: dict[str, dict[str, Any]] = defaultdict(dict)
    found_keys: set[str] = set()
    for property_name in flattened_property_names:
        for key, value in mapping.items():
            prefix = f"{property_name}."
            if key.startswith(prefix):
                unprefixed_key = key[len(prefix) :]
                flattened_mappings[property_name][unprefixed_key] = mapping[key]
                found_keys.add(key)
    return dict(
        **{k: v for k, v in mapping.items() if k not in found_keys},
        **flattened_mappings,
    )


def normalize_name_set(names: str | Sequence[str]) -> set[str]:
    if isinstance(names, str):
        return {names} if names else set()
    elif isinstance(names, (list, tuple, set)):
        return set(n for n in names if n)
    raise TypeError("flatten_names must be a str or a sequence of str")
