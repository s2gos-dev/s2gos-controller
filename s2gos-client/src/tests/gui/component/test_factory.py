#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase
import panel as pn

from s2gos_client.gui.component import (
    Component,
    ComponentFactory,
    JsonValue,
    JsonSchemaDict,
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
    def test_get_relevance(self):
        class Factory(FactoryBase):
            base_schema = dict(type="string", format="date", nullable=True)

        f = Factory()
        self.assertEqual(0, f.get_score(dict()))
        self.assertEqual(0, f.get_score(dict(type="integer", nullable=True)))
        self.assertEqual(0, f.get_score(dict(type="string", nullable=True)))
        self.assertEqual(0, f.get_score(dict(type="string", format="bbox")))
        self.assertEqual(0, f.get_score(dict(type="string", format="date ")))
        self.assertEqual(
            16, f.get_score(dict(type="string", format="date", nullable=True))
        )

    # noinspection PyMethodMayBeStatic,PyTypeChecker
    def test_register_in(self):
        class GoodFactory0(FactoryBase):
            pass

        class GoodFactory1(FactoryBase):
            base_schema = dict(type="string")

        class GoodFactory2(FactoryBase):
            base_schema = dict(type="string", format="date")

        class GoodFactory3(FactoryBase):
            base_schema = dict(type="string", format="date", nullable=True)

        registry = MockRegistry()
        GoodFactory0.register_in(registry)
        GoodFactory1.register_in(registry)
        GoodFactory2.register_in(registry)
        GoodFactory3.register_in(registry)
        self.assertEqual(
            [
                {"type": None},
                {"type": "string"},
                {"type": "string"},
                {"type": "string"},
            ],
            [kwargs for _args, kwargs in registry.registrations],
        )
        self.assertIsInstance(registry.registrations[0][0][0], GoodFactory0)
        self.assertIsInstance(registry.registrations[1][0][0], GoodFactory1)
        self.assertIsInstance(registry.registrations[2][0][0], GoodFactory2)
        self.assertIsInstance(registry.registrations[3][0][0], GoodFactory3)
