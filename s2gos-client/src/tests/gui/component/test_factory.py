#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import panel as pn

from s2gos_client.gui.component import (
    Component,
    ComponentFactory,
    JsonSchemaDict,
    JsonValue,
)


class FactoryBase(ComponentFactory):
    def create_component(
        self, json_value: JsonValue, title: str, schema: JsonSchemaDict
    ) -> Component:
        return Component(pn.widgets.TextInput(value=json_value, name=title))


class MockRegistry:
    def __init__(self):
        self.registrations = []

    def register_factory(self, *args, **kwargs):
        self.registrations.append((args, kwargs))


class ComponentFactoryTest(TestCase):
    def test_get_score(self):
        class Factory(FactoryBase):
            type = "string"

        f = Factory()
        self.assertEqual(0, f.get_score(dict()))
        self.assertEqual(0, f.get_score(dict(type="integer")))
        self.assertEqual(1, f.get_score(dict(type="string")))

    # noinspection PyMethodMayBeStatic,PyTypeChecker
    def test_register_in(self):
        class GoodFactory0(FactoryBase):
            pass

        class GoodFactory1(FactoryBase):
            type = "string"

        class GoodFactory2(FactoryBase):
            type = "integer"

        class GoodFactory3(FactoryBase):
            type = "boolean"

        registry = MockRegistry()
        GoodFactory0.register_in(registry)
        GoodFactory1.register_in(registry)
        GoodFactory2.register_in(registry)
        GoodFactory3.register_in(registry)
        self.assertEqual(
            [{}, {}, {}, {}],
            [kwargs for _args, kwargs in registry.registrations],
        )
        self.assertIsInstance(registry.registrations[0][0][0], GoodFactory0)
        self.assertIsInstance(registry.registrations[1][0][0], GoodFactory1)
        self.assertIsInstance(registry.registrations[2][0][0], GoodFactory2)
        self.assertIsInstance(registry.registrations[3][0][0], GoodFactory3)
