#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
from typing import Any

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
