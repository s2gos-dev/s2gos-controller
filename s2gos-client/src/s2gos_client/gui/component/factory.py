#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .component import Component
from .types import JsonSchema, JsonType, JsonValue

if TYPE_CHECKING:
    from .registry import ComponentFactoryRegistry


class ComponentFactory(ABC):
    """Factory for components."""

    @abstractmethod
    def create_component(
        self, json_value: JsonValue, title: str, schema: JsonSchema
    ) -> Component:
        """Create a new component from given JSON schema."""

    @abstractmethod
    def get_relevance(self, schema: JsonSchema) -> int | float | None:
        """Get the relevance of this factory for the given JSON schema."""

    @classmethod
    def register_in(cls, registry: "ComponentFactoryRegistry"):
        """Register this provider in the given registry."""
        registry.register_factory(cls())


class TypedComponentFactory(ComponentFactory, ABC):
    type: JsonType
    format: str | None = None
    nullable: bool | None = None

    def get_relevance(self, schema: JsonSchema) -> int | None:
        type_ = schema.get("type")
        format_ = schema.get("format")
        nullable = schema.get("nullable", False)
        applicable = (
            self.type == type_
            and self.format == format_
            and (self.nullable is None or self.nullable == nullable)
        )
        return 1 if applicable else None

    @classmethod
    def register_in(cls, registry: "ComponentFactoryRegistry"):
        registry.register_factory(
            cls(), type=cls.type, format=cls.format, nullable=cls.nullable
        )
