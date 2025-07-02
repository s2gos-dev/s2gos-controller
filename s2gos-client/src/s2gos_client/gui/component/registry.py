#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from collections import defaultdict
from typing import TypeAlias

from .factory import ComponentFactory
from .types import JsonSchema, JsonType

_RegistryKey: TypeAlias = tuple[JsonType | None, str | None, bool | None]


# noinspection PyShadowingBuiltins
class ComponentFactoryRegistry:
    def __init__(self):
        self._factories: dict[_RegistryKey, list[ComponentFactory]] = defaultdict(list)

    def register_factory(
        self,
        factory: ComponentFactory,
        *,
        type: JsonType | None = None,
        format: str | None = None,
        nullable: bool | None = None,
    ):
        self._factories[(type, format, nullable)].append(factory)

    def find_factory(self, schema: JsonSchema) -> ComponentFactory | None:
        type = schema.get("type")
        format = schema.get("format")
        nullable = schema.get("nullable")
        factories = self._get_factories(type, format, nullable)
        if not factories and type:
            factories = self._get_factories(None, format, nullable)
            if not factories and format:
                factories = self._get_factories(None, None, nullable)
                if not factories and nullable is not None:
                    factories = self._get_factories(None, None, None)
        return self._select_most_relevant_factory(factories, schema)

    def _get_factories(self, *key) -> list[ComponentFactory] | None:
        # noinspection PyTypeChecker
        return self._factories.get(key)

    @classmethod
    def _select_most_relevant_factory(
        cls, factories: list[ComponentFactory] | None, schema: JsonSchema
    ) -> ComponentFactory | None:
        if factories:
            relevant_factories = []
            for f in factories:
                r = f.get_relevance(schema)
                if isinstance(r, (int, float)):
                    relevant_factories.append((f, r))
            if len(relevant_factories) > 1:
                relevant_factories = sorted(
                    relevant_factories, key=lambda item: item[1]
                )
                return relevant_factories[0][0]
        return None
