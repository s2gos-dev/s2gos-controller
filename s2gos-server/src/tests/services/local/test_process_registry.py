#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import pytest
from pydantic import BaseModel, Field

from s2gos_common.models import (
    DataType,
    InputDescription,
    OutputDescription,
    ProcessDescription,
    Schema,
)
from s2gos_common.testing import BaseModelMixin
from s2gos_server.services.local import ProcessRegistry, RegisteredProcess


def f1(x: bool, y: int) -> float:
    """This is f1."""
    return 2.0 * y if x else 0.5 * y


def f2(a: bool | None, b: float | bool) -> tuple[float, float]:
    """This is f2."""
    return (2.0 * b, 0.5 * b) if a else (0.5 * b, 2.0 * b)


class Point(BaseModel):
    """A 2-D point."""

    x: float = Field(0.0, title="X-coordinate")
    y: float = Field(0.0, title="Y-coordinate")


def f3(point1: Point, point2: Point) -> Point:
    """This is f3."""
    return Point(x=(point2.x - point1.x), y=(point2.y - point1.y))


class ProcessRegistryTest(BaseModelMixin, TestCase):
    def test_register_f1(self):
        registry = ProcessRegistry()

        entry = registry.register_function(f1)
        self.assertIsInstance(entry, RegisteredProcess)
        self.assertIs(f1, entry.function)
        process = entry.description
        self.assertIsInstance(process, ProcessDescription)
        self.assertEqual("f1", process.id)
        self.assertEqual("0.0.0", process.version)
        self.assertEqual(None, process.title)
        self.assertEqual("This is f1.", process.description)
        inputs = process.inputs
        outputs = process.outputs
        self.assertIsInstance(inputs, dict)
        self.assertIsInstance(outputs, dict)
        self.assertEqual(["x", "y"], list(inputs.keys()))
        self.assertEqual(["return_value"], list(outputs.keys()))
        self.assertBaseModelEqual(
            InputDescription(title="X", schema=Schema(type=DataType.boolean)),
            inputs["x"],
        )
        self.assertBaseModelEqual(
            InputDescription(title="Y", schema=Schema(type=DataType.integer)),
            inputs["y"],
        )
        self.assertEqual(
            OutputDescription(
                title="Return Value",
                schema=Schema(type=DataType.number),
            ),
            outputs["return_value"],
        )

    def test_register_f2(self):
        registry = ProcessRegistry()

        entry = registry.register_function(f2)
        self.assertIsInstance(entry, RegisteredProcess)
        self.assertIs(f2, entry.function)
        process = entry.description
        self.assertIsInstance(process, ProcessDescription)
        self.assertEqual("f2", process.id)
        self.assertEqual("0.0.0", process.version)
        self.assertEqual(None, process.title)
        self.assertEqual("This is f2.", process.description)
        inputs = process.inputs
        outputs = process.outputs
        self.assertIsInstance(inputs, dict)
        self.assertIsInstance(outputs, dict)
        self.assertEqual(["a", "b"], list(inputs.keys()))
        self.assertEqual(["return_value"], list(outputs.keys()))
        self.assertBaseModelEqual(
            InputDescription(
                title="A",
                schema=Schema(type=DataType.boolean, nullable=True),
            ),
            inputs["a"],
        )
        self.assertBaseModelEqual(
            InputDescription(
                title="B",
                schema=Schema(
                    anyOf=[
                        Schema(type=DataType.number),
                        Schema(type=DataType.boolean),
                    ],
                ),
            ),
            inputs["b"],
        )
        self.assertBaseModelEqual(
            OutputDescription(
                title="Return Value",
                schema=Schema(
                    type=DataType.array,
                    items=Schema(type="number"),
                    minItems=2,
                    maxItems=2,
                ),
            ),
            outputs["return_value"],
        )

    def test_register_f2_with_1_output_field(self):
        registry = ProcessRegistry()

        entry = registry.register_function(
            f2,
            output_fields={
                "point": Field(title="A point (x, y)"),
            },
        )
        self.assertIsInstance(entry, RegisteredProcess)
        self.assertIs(f2, entry.function)
        process = entry.description
        self.assertIsInstance(process, ProcessDescription)
        self.assertEqual("f2", process.id)
        self.assertEqual("0.0.0", process.version)
        self.assertEqual(None, process.title)
        self.assertEqual("This is f2.", process.description)
        inputs = process.inputs
        outputs = process.outputs
        self.assertIsInstance(inputs, dict)
        self.assertIsInstance(outputs, dict)
        self.assertEqual(["a", "b"], list(inputs.keys()))
        self.assertEqual(["point"], list(outputs.keys()))
        self.assertBaseModelEqual(
            OutputDescription(
                title="A point (x, y)",
                schema=Schema(
                    type=DataType.array,
                    items=Schema(type="number"),
                    minItems=2,
                    maxItems=2,
                ),
            ),
            outputs["point"],
        )

    def test_register_f2_with_2_output_fields(self):
        registry = ProcessRegistry()

        entry = registry.register_function(
            f2,
            output_fields={
                "x": Field(title="The X", ge=0.0),
                "y": Field(title="The Y", lt=1.0),
            },
        )
        self.assertIsInstance(entry, RegisteredProcess)
        self.assertIs(f2, entry.function)
        process = entry.description
        self.assertIsInstance(process, ProcessDescription)
        self.assertEqual("f2", process.id)
        self.assertEqual("0.0.0", process.version)
        self.assertEqual(None, process.title)
        self.assertEqual("This is f2.", process.description)
        inputs = process.inputs
        outputs = process.outputs
        self.assertIsInstance(inputs, dict)
        self.assertIsInstance(outputs, dict)
        self.assertEqual(["a", "b"], list(inputs.keys()))
        self.assertEqual(["x", "y"], list(outputs.keys()))
        self.assertBaseModelEqual(
            OutputDescription(
                title="The X",
                schema=Schema(type=DataType.number, minimum=0.0),
            ),
            outputs["x"],
        )
        self.assertEqual(
            OutputDescription(
                title="The Y",
                schema=Schema(type=DataType.number, exclusiveMaximum=1.0),
            ),
            outputs["y"],
        )

    # noinspection PyMethodMayBeStatic
    def test_register_illegal_f1_with_output_fields(self):
        registry = ProcessRegistry()
        with pytest.raises(
            TypeError,
            match=(
                r"function 'tests.services.local.test_process_registry\:f1'\: "
                r"return type must be tuple\[\] with arguments"
            ),
        ):
            registry.register_function(
                f1,
                output_fields={
                    "x": Field(title="The X", ge=0.0),
                    "y": Field(title="The Y", lt=1.0),
                },
            )

    # noinspection PyMethodMayBeStatic
    def test_register_f1_with_illegal_input_fields(self):
        registry = ProcessRegistry()
        with pytest.raises(
            ValueError,
            match=(
                r"function tests\.services\.local\.test_process_registry\:f1\: "
                r"all input names must have corresponding parameter names; "
                r"invalid input name\(s\)\: 'u', 'v'"
            ),
        ):
            registry.register_function(
                f1,
                input_fields={
                    "x": Field(title="The valid X", ge=0.0),
                    "y": Field(title="The valid Y", lt=1.0),
                    "u": Field(title="The illegal U"),
                    "v": Field(title="The illegal V"),
                },
            )

    # noinspection PyMethodMayBeStatic
    def test_register_f2_with_illegal_output_fields(self):
        registry = ProcessRegistry()
        with pytest.raises(
            ValueError,
            match=(
                r"function 'tests.services.local.test_process_registry\:f2'\: "
                r"number of outputs must match number of tuple\[\] arguments"
            ),
        ):
            registry.register_function(
                f2,
                output_fields={
                    "x": Field(title="The X", ge=0.0),
                    "y": Field(title="The Y", lt=1.0),
                    "z": Field(title="The Z"),
                },
            )

    def test_register_f1_with_props(self):
        registry = ProcessRegistry()

        e1 = registry.register_function(f1, id="foo", version="1.0.2", title="My Foo")
        self.assertIsInstance(e1, RegisteredProcess)
        self.assertIs(f1, e1.function)
        p1 = e1.description
        self.assertIsInstance(p1, ProcessDescription)
        self.assertEqual("foo", p1.id)
        self.assertEqual("1.0.2", p1.version)
        self.assertEqual("My Foo", p1.title)
        self.assertEqual("This is f1.", p1.description)
        self.assertIsInstance(p1.inputs, dict)
        self.assertIsInstance(p1.outputs, dict)

    def test_register_f3(self):
        registry = ProcessRegistry()

        entry = registry.register_function(f3, id="f3")
        self.assertEqual(
            {"point1", "point2"},
            set(entry.description.inputs.keys()),
        )
        self.assertBaseModelEqual(
            InputDescription(
                title="Point",
                description="A 2-D point.",
                schema=Schema(
                    **{
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "number",
                                "default": 0.0,
                                "title": "X-coordinate",
                            },
                            "y": {
                                "type": "number",
                                "default": 0.0,
                                "title": "Y-coordinate",
                            },
                        },
                    }
                ),
            ),
            entry.description.inputs["point1"],
        )

    def test_register_multiple(self):
        registry = ProcessRegistry()
        self.assertEqual([], list(registry.keys()))
        self.assertEqual(None, registry.get("f1"))

        registry.register_function(f1)
        self.assertEqual(1, len(registry))
        p1 = list(registry.values())[0]
        self.assertIsInstance(p1, RegisteredProcess)
        self.assertIs(p1, registry.get(p1.description.id))

        registry.register_function(f2)
        self.assertEqual(2, len(registry))
        p1, p2 = registry.values()
        self.assertIsInstance(p1, RegisteredProcess)
        self.assertIsInstance(p2, RegisteredProcess)
        self.assertIs(p1, registry.get(p1.description.id))
        self.assertIs(p2, registry.get(p2.description.id))
