#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

import panel as pn

from .types import JsonType, JsonSchema, JsonValue

if TYPE_CHECKING:
    from .registry import ViewableProviderRegistry


class ViewableProvider(ABC):
    @abstractmethod
    def get_viewable(
        self, schema: JsonSchema, **extras: JsonValue
    ) -> pn.viewable.Viewable:
        """
        Get a widget for a given schema.

        Args:
            schema: the JSON schema dictionary
            extras: derived values not necessarily contained in the schema,
                e.g., `title` and `value`


        Returns: An instance of `panel.viewable.Viewable`
        """

    @abstractmethod
    def get_schema_relevance(self, schema: JsonSchema) -> int | None:
        """Get the relevance of a given schema for this provider."""

    @abstractmethod
    def get_json_value(self, viewable: pn.viewable.Viewable) -> JsonValue:
        """Get the current JSON value that `viewable` represents."""

    @abstractmethod
    def set_json_value(self, viewable: pn.viewable.Viewable, value: JsonValue) -> Any:
        """Set the current JSON value so that `viewable` represents it."""

    @classmethod
    def register_in(cls, registry: "ViewableProviderRegistry"):
        """Register this provider in the given registry."""
        registry.register_provider(cls())


# noinspection PyShadowingBuiltins
class TypedViewableProvider(ViewableProvider, ABC):
    type: JsonType
    format: str | None = None
    nullable: bool | None = None

    def get_schema_relevance(self, schema: JsonSchema) -> int | None:
        type = schema.get("type")
        format = schema.get("format")
        nullable = schema.get("nullable", False)
        applicable = (
            self.type == type
            and self.format == format
            and (self.nullable is None or self.nullable == nullable)
        )
        return 1 if applicable else None

    @classmethod
    def register_in(cls, registry: "ViewableProviderRegistry"):
        registry.register_provider(
            cls(), type=cls.type, format=cls.format, nullable=cls.nullable
        )


# noinspection PyMethodMayBeStatic
class WidgetViewableProvider(TypedViewableProvider, ABC):
    def get_viewable(
        self, schema: JsonSchema, **extras: JsonValue
    ) -> pn.widgets.Widget:
        widget = self.get_widget(schema, **extras)
        assert isinstance(widget, pn.widgets.Widget)
        return widget

    @abstractmethod
    def get_widget(self, schema: JsonSchema, **extras: JsonValue) -> pn.widgets.Widget:
        """ """

    def get_json_value(self, /, widget: pn.widgets.Widget) -> Any:
        return widget.value

    def set_json_value(self, /, widget: pn.widgets.Widget, value: JsonValue) -> Any:
        widget.value = value
