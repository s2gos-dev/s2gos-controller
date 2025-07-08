#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import datetime
from typing import Any, Callable

import panel as pn

from .bbox import BboxSelector
from .component import Component, WidgetComponent
from .factory import ComponentFactoryBase
from .json import JsonDateCodec, JsonSchemaDict
from .registry import ComponentFactoryRegistry


class BooleanComponentFactory(ComponentFactoryBase):
    type = "boolean"

    def create_component(
        self, value: bool, title: str, schema: JsonSchemaDict
    ) -> Component:
        value = value if value is not None else False
        return WidgetComponent(
            pn.widgets.Checkbox(name=title, value=value),
        )


class IntegerComponentFactory(ComponentFactoryBase):
    type = "integer"

    def create_component(
        self, value: int, title: str, schema: JsonSchemaDict
    ) -> Component:
        value = value if value is not None else 0
        return WidgetComponent(
            pn.widgets.IntSlider(
                name=title,
                start=int(schema.get("minimum", 0)),
                end=int(schema.get("maximum", 100)),
                value=value,
                step=1,
            )
        )


class NumberComponentFactory(ComponentFactoryBase):
    type = "number"

    def create_component(
        self, value: int | float, title: str, schema: JsonSchemaDict
    ) -> Component:
        value = value if value is not None else 0.0
        # noinspection PyTypeChecker
        return WidgetComponent(
            pn.widgets.FloatSlider(
                name=title,
                start=float(schema.get("minimum", 0)),
                end=float(schema.get("maximum", 100)),
                value=float(value),
                step=1,
            )
        )


class StringComponentFactory(ComponentFactoryBase):
    type = "string"

    def create_component(self, value, title, schema: JsonSchemaDict) -> Component:
        value = value or ""
        if "enum" in schema:
            widget = pn.widgets.Select(name=title, options=schema["enum"], value=value)
        else:
            widget = pn.widgets.TextInput(name=title, value=value)
        return WidgetComponent(widget)


class DateComponentFactory(ComponentFactoryBase):
    type = "string"
    format = "date"

    def create_component(
        self, value: str, title: str, schema: JsonSchemaDict
    ) -> Component:
        json_codec = JsonDateCodec()
        date = json_codec.to_json(value) or datetime.date.today()
        return WidgetComponent(
            pn.widgets.DatePicker(name=title, value=date), json_codec=json_codec
        )


class BboxComponentFactory(ComponentFactoryBase):
    type = "array"
    format = "bbox"

    def create_component(self, value, title, schema: JsonSchemaDict) -> Component:
        selector = BboxSelector()
        # TODO: set value & title
        return BboxComponent(selector)


class BboxComponent(Component):
    def __init__(self, bbox_selector: BboxSelector):
        super().__init__(bbox_selector)

    @property
    def bbox_selector(self) -> BboxSelector:
        # noinspection PyTypeChecker
        return self.viewable

    def get_value(self) -> Any:
        return self.bbox_selector.value

    def set_value(self, value: Any):
        self.bbox_selector.value = value

    def watch_value(self, callback: Callable[[Any, Any], Any]):
        self.bbox_selector.param.watch(callback, "value")


def register_all(registry: ComponentFactoryRegistry):
    BooleanComponentFactory.register_in(registry)
    IntegerComponentFactory.register_in(registry)
    NumberComponentFactory.register_in(registry)
    StringComponentFactory.register_in(registry)
    DateComponentFactory.register_in(registry)
    BboxComponentFactory.register_in(registry)
