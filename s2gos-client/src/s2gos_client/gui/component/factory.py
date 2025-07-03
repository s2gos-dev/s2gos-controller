#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .component import Component
from .json import JsonSchemaDict, JsonValue

if TYPE_CHECKING:
    from .registry import ComponentFactoryRegistry


class ComponentFactory(ABC):
    """Factory for components."""

    base_schema: JsonSchemaDict = {}
    """Specifies required schema values."""

    @abstractmethod
    def create_component(
        self, json_value: JsonValue, title: str, schema: JsonSchemaDict
    ) -> Component:
        """Create a new component from given JSON schema."""

    def get_score(self, schema: JsonSchemaDict) -> int:
        """
        Get a score of how well the components produced by this factory
        can represent the given schema.
        """
        scores = {"type": 10, "format": 5}
        defaults = {"nullable": False}
        score = 0
        for k, v in self.base_schema.items():
            if v != schema.get(k, defaults.get(k)):
                return 0
            score += scores.get(k, 1)
        return score

    @classmethod
    def register_in(cls, registry: "ComponentFactoryRegistry"):
        """Register this factory in the given registry."""
        registry.register_factory(cls(), type=cls.base_schema.get("type"))
