#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from collections import defaultdict

from .factory import ComponentFactory
from .json import JSON_TYPE_NAMES, JsonSchemaDict, JsonType


class ComponentFactoryRegistry:
    def __init__(self):
        self._factories: dict[JsonType | None, list[ComponentFactory]] = defaultdict(
            list
        )

    def register_factory(
        self,
        factory: ComponentFactory,
    ):
        key = factory.type
        if key is not None and key not in JSON_TYPE_NAMES:
            raise ValueError(
                f"Factory type must be one of {JSON_TYPE_NAMES}, was {key!r}"
            )
        self._factories[key].append(factory)

    def find_factory(self, schema: JsonSchemaDict) -> ComponentFactory | None:
        key = schema.get("type")
        candidate_factories = self._factories.get(key)
        if not candidate_factories:
            return None
        if len(candidate_factories) == 1:
            return candidate_factories[0]
        best_factory: ComponentFactory | None = None
        best_r = 0
        # we reverse to force LIFO
        for factory in reversed(candidate_factories):
            r = factory.get_score(schema)
            if r > best_r:
                best_r = r
                best_factory = factory
        return best_factory
