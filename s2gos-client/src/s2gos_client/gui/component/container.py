#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import warnings
from dataclasses import dataclass
from typing import Any, Callable

from s2gos_common.models import InputDescription, Schema

from .component import Component
from .impl import register_all
from .registry import ComponentFactoryRegistry
from .json import JsonSchemaDict, JsonValue


class ComponentContainer:
    registry = ComponentFactoryRegistry()

    @dataclass
    class Item:
        schema: JsonSchemaDict
        # TODO: check if we need value
        value: JsonValue
        component: Component

    @classmethod
    def from_input_descriptions(
        cls,
        input_descriptions: dict[str, InputDescription],
        json_values: dict[str, JsonValue],
    ) -> "ComponentContainer":
        schemas: JsonSchemaDict = {}
        for k, v in input_descriptions.items():
            schema = _get_schema_from_input_description(v)
            if schema is not None:
                schemas[k] = schema
            else:
                warnings.warn(f"Cannot get usable JSON schema from input {k!r}.")
        return cls(schemas, json_values)

    def __init__(
        self, schemas: dict[str, JsonSchemaDict], json_values: dict[str, JsonValue]
    ):
        self._entries: dict[str, ComponentContainer.Item] = {}
        for name, schema in schemas.items():
            factory = self.registry.find_factory(schema)
            if factory is None:
                warnings.warn(f"Cannot create component for input {name!r}")
                continue
            value = json_values.get(name, schemas.get("default"))
            title = schema.get("title") or _get_title_from_name(name)
            component = factory.create_component(value, title, schema)
            # TODO: check if we need this
            component.watch_value(self._get_on_value_changed(name, component))
            self._entries[name] = ComponentContainer.Item(schema, value, component)

    def get_json_values(self):
        """Get component values as JSON values."""
        return {
            name: entry.component.get_json_value()
            for name, entry in self._entries.items()
        }

    def set_json_values(self, json_values: dict[str, JsonValue]):
        """Set component values from JSON values."""
        return {
            name: entry.component.set_json_value(json_values)
            for name, entry in self._entries.items()
            if name in json_values
        }

    def get_components(self) -> list[Component]:
        return [entry.component for entry in self._entries.values()]

    def _get_on_value_changed(self, name: str, component: Component) -> Callable:
        def on_value_changed(_event: Any, new_value: Any):
            json_value = component.json_codec.encode(new_value)
            self._entries[name].value = json_value

        return on_value_changed


register_all(ComponentContainer.registry)


def _get_title_from_name(name: str) -> str:
    return name.capitalize().replace("-", " ").replace("_", " ")


def _get_schema_from_input_description(
    input_description: InputDescription,
) -> JsonSchemaDict | None:
    v = input_description
    if not isinstance(v.schema_, Schema):
        return None
    schema = v.schema_.model_dump(
        mode="json", exclude_defaults=True, exclude_none=True, by_alias=True
    )
    is_scalar = v.minOccurs == 1 and (v.maxOccurs is None or v.maxOccurs == 1)
    if not is_scalar:
        schema = {
            "type": "array",
            "items": schema,
            "minItems": (v.minOccurs if isinstance(v.minOccurs, int) else None),
            "maxItems": (v.maxOccurs if isinstance(v.maxOccurs, int) else None),
        }
    if v.title:
        schema["title"] = v.title
    if v.description:
        schema["description"] = v.description
    return schema
