#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .component import Component
from .json import JsonSchemaDict, JsonType, JsonValue

if TYPE_CHECKING:
    from .registry import ComponentFactoryRegistry


class ComponentFactory(ABC):
    """Factory for components."""

    @abstractmethod
    def create_component(
        self, value: JsonValue, title: str, schema: JsonSchemaDict
    ) -> Component:
        """
        Create a new component from given JSON schema.

        Args:
            value: the initial JSON input value, may be `None`
            title: a component title
            schema: the schema

        Returns: a component
        """

    @abstractmethod
    def get_score(self, schema: JsonSchemaDict) -> int:
        """
        Get a score of how well the components produced by this factory
        can represent the given schema.
        """

    # noinspection PyShadowingBuiltins
    @staticmethod
    def get_key(type: str | None, format: str | None) -> str:
        """
        Get a key for given JSON data type name `type` and `format`.
        """
        type_key = type if type else "*"
        format_key = format if format else "*"
        return f"{type_key}.{format_key}"


class ComponentFactoryBase(ComponentFactory, ABC):
    """Factory for components."""

    type: JsonType | None = None
    """Specifies the JSON type to use as a registry key."""

    format: str | None = None
    """Specifies the JSON type to use as a registry key."""

    # noinspection PyShadowingBuiltins
    def get_score(self, schema: JsonSchemaDict) -> int:
        type = schema.get("type")
        format = schema.get("format")
        if self.type and self.type == type:
            if self.format:
                return 2 if self.format == format else 0
            return 1
        return 0

    @classmethod
    def register_in(cls, registry: "ComponentFactoryRegistry"):
        """Register this factory in the given registry."""
        registry.register_factory(cls(), type=cls.type, format=cls.format)
