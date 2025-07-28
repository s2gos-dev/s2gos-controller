#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos_common.process import ProcessRegistry, RegisteredProcess
from s2gos_common.testing import BaseModelMixin

from .test_registered_process import f1, f2, f3


class ProcessRegistryTest(BaseModelMixin, TestCase):
    def test_register_function(self):
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

    def test_to_json_dict(self):
        self.maxDiff = None
        registry = ProcessRegistry()
        registry.register_function(f1)
        registry.register_function(f2)
        registry.register_function(f3)

        json_dict = registry.to_json_dict()
        self.assertEqual({"f1", "f2", "f3"}, set(json_dict.keys()))
        f1_entry = json_dict["f1"]
        self.assertEqual(
            {
                "id": "f1",
                "version": "0.0.0",
                "description": "This is f1.",
                "inputs": {
                    "x": {"schema": {"type": "boolean"}, "title": "X"},
                    "y": {"schema": {"type": "integer"}, "title": "Y"},
                },
                "outputs": {
                    "return_value": {
                        "schema": {"type": "number"},
                        "title": "Return Value",
                    }
                },
            },
            f1_entry,
        )

        json_dict = registry.to_json_dict(use_qual_names=True)
        self.assertEqual(
            {
                "tests.process.test_registered_process:f1",
                "tests.process.test_registered_process:f2",
                "tests.process.test_registered_process:f3",
            },
            set(json_dict.keys()),
        )
        self.assertEqual(
            f1_entry, json_dict["tests.process.test_registered_process:f1"]
        )

    def test_to_json(self):
        registry = ProcessRegistry()
        registry.register_function(f1)

        json = registry.to_json()
        self.assertTrue(json.startswith('{"f1": {"'))

        json = registry.to_json(use_qual_names=True)
        self.assertTrue(
            json.startswith('{"tests.process.test_registered_process:f1": {"')
        )
