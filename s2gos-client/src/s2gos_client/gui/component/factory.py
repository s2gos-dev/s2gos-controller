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

    type: JsonType | None = None
    """Specifies the JSON type to use as a registry key."""

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

    def get_score(self, schema: JsonSchemaDict) -> int:
        """
        Get a score of how well the components produced by this factory
        can represent the given schema.
        """
        return 1 if (self.type and self.type == schema.get("type")) else 0

    @classmethod
    def register_in(cls, registry: "ComponentFactoryRegistry"):
        """Register this factory in the given registry."""
        registry.register_factory(cls())
