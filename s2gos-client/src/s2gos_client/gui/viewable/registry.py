#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from collections import defaultdict
from typing import TypeAlias
from .types import JsonType, JsonSchema
from .provider import ViewableProvider

_RegistryKey: TypeAlias = tuple[JsonType | None, str | None, bool | None]


# noinspection PyShadowingBuiltins
class ViewableProviderRegistry:
    def __init__(self):
        self._providers: dict[_RegistryKey, list[ViewableProvider]] = defaultdict(list)

    def register_provider(
        self,
        provider: ViewableProvider,
        *,
        type: JsonType | None = None,
        format: str | None = None,
        nullable: bool | None = None,
    ):
        self._providers[(type, format, nullable)].append(provider)

    def get_provider(self, schema: JsonSchema) -> ViewableProvider | None:
        type = schema.get("type")
        format = schema.get("format")
        nullable = schema.get("nullable")
        providers = self._get_providers(type, format, nullable)
        if not providers and type:
            providers = self._get_providers(None, format, nullable)
            if not providers and format:
                providers = self._get_providers(None, None, nullable)
                if not providers and nullable is not None:
                    providers = self._get_providers(None, None, None)
        return self._select_relevant_provider(providers, schema)

    def _get_providers(self, *key) -> list[ViewableProvider] | None:
        # noinspection PyTypeChecker
        return self._providers.get(key)

    @classmethod
    def _select_relevant_provider(
        cls, providers: list[ViewableProvider] | None, schema: JsonSchema
    ) -> ViewableProvider | None:
        if providers:
            relevant_providers = []
            for p in providers:
                r = p.get_schema_relevance(schema)
                if r is not None:
                    relevant_providers.append((p, r))
            if relevant_providers:
                relevant_providers = sorted(
                    relevant_providers, key=lambda item: item[1]
                )
                return relevant_providers[0][0]
        return None
