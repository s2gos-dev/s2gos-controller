#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
from abc import ABC, abstractmethod
from typing import Any, Literal, TypeAlias

import panel as pn
import param

from .bbox_selector import BboxSelector

TYPES = "boolean", "integer", "number", "string", "array"
DEFAULTS = {"boolean": False, "integer": 0, "number": 0.0, "string": "", "array": []}

# TODO: Enhance WidgetFactory
#   * WidgetFactory should be configurable by extensions
#   * An extension is an interface
#     - one can set the widget value from a JSON value
#     - one can get the widget value as JSON value
#     - one can get the widget
#     - one can check if a given schema can instantiate the extension
#       from schema (abstract classmethod)

Schema: TypeAlias = dict[str, Any]
JsonType = Literal["boolean", "integer", "number", "string", "array", "object"]


class ViewableProvider(ABC):
    @abstractmethod
    def get_viewable(self, schema: Schema, name: str) -> pn.viewable.Viewable:
        """
        Get a widget for a given schema.

        Args:
            schema: the JSON schema dictionary
            name: the name of a parameter for which the viewable
                is provided
        """

    @abstractmethod
    def is_valid_schema(self, schema: Schema) -> bool:
        """Whether the given schema can be used to provide a viewable."""

    @abstractmethod
    def get_json_value(self, viewable: pn.viewable.Viewable) -> Any:
        """Get the current JSON value that `viewable` represents."""


class ViewableProviderRegistry:
    def __init__(self):
        self._providers: dict[str, dict[str, ViewableProvider]] = {}

    def register(
        self,
        provider: ViewableProvider,
        json_type: JsonType | None = None,
        json_format: str | None = None,
    ):
        type_key = str(json_type) or "*"
        format_key = json_format or "*"
        self._providers[type_key][format_key] = provider

    def get_viewable(self, schema: Schema) -> ViewableProvider | None:
        type_key = schema.get("type") or "*"
        format_key = schema.get("format") or "*"
        provider = self._get_viewable(type_key, format_key)
        if provider is None and type_key != "*":
            provider = self._get_viewable("*", format_key)
        return provider

    def _get_viewable(self, type_key: str, format_key: str) -> ViewableProvider | None:
        format_dict = self._providers.get(type_key)
        if format_dict is not None:
            provider = format_dict.get(format_key)
            if provider is None and format_key != "*":
                return format_dict.get("*")
        return None


class WidgetFactory:
    # noinspection PyMethodMayBeStatic
    def get_widget_for_schema(
        self, param_name: str, param_schema: dict[str, Any], _required: bool
    ) -> param.Parameterized | None:
        return _param_schema_to_widget(param_name, param_schema, _required)


def _param_schema_to_widget(
    param_name: str, param_schema: dict[str, Any], _required: bool
) -> param.Parameterized | None:
    """Naive implementation of a mapping from schema to panel widget."""
    if "type" not in param_schema:
        raise ValueError("missing 'type' property")
    type_ = param_schema["type"]
    if not isinstance(type_, str) or type_ not in TYPES:
        raise ValueError(
            f"value of 'type' property must be one of {TYPES}, was {type_!r}"
        )

    title = param_schema.get("title", param_name.replace("_", " ").capitalize())
    value = param_schema.get("default", DEFAULTS.get(type_))

    if type_ == "boolean":
        return pn.widgets.Checkbox(name=title, value=value)

    if type_ == "integer":
        return pn.widgets.IntSlider(
            name=title,
            start=int(param_schema.get("minimum", 0)),
            end=int(param_schema.get("maximum", 100)),
            value=int(value),
            step=1,
        )
    if type_ == "number":
        return pn.widgets.FloatSlider(
            name=title,
            start=param_schema.get("minimum", 0),
            end=param_schema.get("maximum", 100),
            value=value,
            step=1,
        )

    if type_ == "string":
        if "enum" in param_schema:
            return pn.widgets.Select(
                name=title, options=param_schema["enum"], value=value
            )
        elif param_schema.get("format") == "date":
            date = (
                datetime.date.fromisoformat(value) if value else datetime.date.today()
            )
            return pn.widgets.DatePicker(name=title, value=date)
        else:
            return pn.widgets.TextInput(name=title, value=value)

    if type_ == "array":
        if param_schema.get("format") == "bbox":
            return BboxSelector(name=title)

    return None
