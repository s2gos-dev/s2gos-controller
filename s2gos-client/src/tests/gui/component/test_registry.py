#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import panel as pn

from s2gos_client.gui.component import (
    Component,
    ComponentFactory,
    ComponentFactoryRegistry,
    JsonSchemaDict,
    JsonValue,
)


class FactoryBase(ComponentFactory):
    def create_component(
        self, json_value: JsonValue, title: str, schema: JsonSchemaDict
    ) -> Component:
        return Component(pn.widgets.TextInput(value=json_value, name=title))


class ComponentFactoryRegistryTest(TestCase):
    def test_register_and_find(self):
        class Factory0(FactoryBase):
            pass

        class Factory1(FactoryBase):
            type = "string"

        class Factory2(FactoryBase):
            type = "string"

            def get_score(self, schema: JsonSchemaDict) -> int:
                return 2 if schema.get("format") == "date" else 0

        class Factory3(FactoryBase):
            type = "string"

            def get_score(self, schema: JsonSchemaDict) -> int:
                return 2 if schema.get("format") == "bbox" else 0

        registry = ComponentFactoryRegistry()

        factory = registry.find_factory(dict(type="string"))
        self.assertIsNone(factory)

        Factory3.register_in(registry)
        Factory0.register_in(registry)
        Factory2.register_in(registry)
        Factory1.register_in(registry)

        factory = registry.find_factory(dict(type="string", format="bbox"))
        self.assertIsInstance(factory, Factory3)

        factory = registry.find_factory(dict(type="string", format="date"))
        self.assertIsInstance(factory, Factory2)

        factory = registry.find_factory(dict(type="string"))
        self.assertIsInstance(factory, Factory1)

        factory = registry.find_factory(dict())
        self.assertIsInstance(factory, Factory0)
