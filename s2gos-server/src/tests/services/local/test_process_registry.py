#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from tests.helpers import BaseModelMixin

from s2gos_common.models import (
    DataType,
    InputDescription,
    OutputDescription,
    ProcessDescription,
    Schema,
)
from s2gos_server.services.local import ProcessRegistry


def f1(x: bool, y: int) -> float:
    """This is f1."""
    return 2.0 * y if x else 0.5 * y


def f2(a: bool | None, b: float | bool) -> tuple[float, float]:
    """This is f2."""
    return (2.0 * b, 0.5 * b) if a else (0.5 * b, 2.0 * b)


class ProcessRegistryTest(BaseModelMixin, TestCase):
    def test_register_f1(self):
        registry = ProcessRegistry()

        entry = registry.register_function(f1)
        self.assertIsInstance(entry, ProcessRegistry.Entry)
        self.assertIs(f1, entry.function)
        process = entry.process
        self.assertIsInstance(process, ProcessDescription)
        self.assertEqual("tests.services.local.test_process_registry:f1", process.id)
        self.assertEqual("0.0.0", process.version)
        self.assertEqual(None, process.title)
        self.assertEqual("This is f1.", process.description)
        inputs = process.inputs
        outputs = process.outputs
        self.assertIsInstance(inputs, dict)
        self.assertIsInstance(outputs, dict)
        self.assertEqual(["x", "y"], list(inputs.keys()))
        self.assertEqual(["result"], list(outputs.keys()))
        self.assertBaseModelEqual(
            InputDescription(schema=Schema(type=DataType.boolean)), inputs["x"]
        )
        self.assertBaseModelEqual(
            InputDescription(schema=Schema(type=DataType.integer)), inputs["y"]
        )
        self.assertEqual(
            OutputDescription(schema=Schema(type=DataType.number)),
            outputs["result"],
        )

    def test_register_f2(self):
        registry = ProcessRegistry()

        entry = registry.register_function(f2)
        self.assertIsInstance(entry, ProcessRegistry.Entry)
        self.assertIs(f2, entry.function)
        process = entry.process
        self.assertIsInstance(process, ProcessDescription)
        self.assertEqual("tests.services.local.test_process_registry:f2", process.id)
        self.assertEqual("0.0.0", process.version)
        self.assertEqual(None, process.title)
        self.assertEqual("This is f2.", process.description)
        inputs = process.inputs
        outputs = process.outputs
        self.assertIsInstance(inputs, dict)
        self.assertIsInstance(outputs, dict)
        self.assertEqual(["a", "b"], list(inputs.keys()))
        self.assertEqual(["result_0", "result_1"], list(outputs.keys()))
        self.assertBaseModelEqual(
            InputDescription(schema=Schema(type=DataType.boolean, nullable=True)),
            inputs["a"],
        )
        self.assertBaseModelEqual(
            InputDescription(
                schema=Schema(
                    oneOf=[Schema(type=DataType.number), Schema(type=DataType.boolean)]
                )
            ),
            inputs["b"],
        )
        self.assertBaseModelEqual(
            OutputDescription(schema=Schema(type=DataType.number)),
            outputs["result_0"],
        )
        self.assertEqual(
            OutputDescription(schema=Schema(type=DataType.number)),
            outputs["result_1"],
        )

    def test_register_f1_with_props(self):
        registry = ProcessRegistry()

        e1 = registry.register_function(f1, id="foo", version="1.0.2", title="My Foo")
        self.assertIsInstance(e1, ProcessRegistry.Entry)
        self.assertIs(f1, e1.function)
        p1 = e1.process
        self.assertIsInstance(p1, ProcessDescription)
        self.assertEqual("foo", p1.id)
        self.assertEqual("1.0.2", p1.version)
        self.assertEqual("My Foo", p1.title)
        self.assertEqual("This is f1.", p1.description)
        self.assertIsInstance(p1.inputs, dict)
        self.assertIsInstance(p1.outputs, dict)

    def test_register_multiple(self):
        registry = ProcessRegistry()

        self.assertEqual([], registry.get_process_list())
        self.assertEqual(None, registry.get_process("f1"))

        registry.register_function(f1)
        self.assertEqual(1, len(registry.get_process_list()))
        p1 = registry.get_process_list()[0]
        self.assertIsInstance(p1, ProcessDescription)
        self.assertIs(p1, registry.get_process(p1.id))

        registry.register_function(f2)
        self.assertEqual(2, len(registry.get_process_list()))
        p1, p2 = registry.get_process_list()
        self.assertIsInstance(p1, ProcessDescription)
        self.assertIsInstance(p2, ProcessDescription)
        self.assertIs(p1, registry.get_process(p1.id))
        self.assertIs(p2, registry.get_process(p2.id))
