#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos_common.process import Process, ProcessRegistry
from s2gos_common.testing import BaseModelMixin

from .test_process import f1, f2, f3


class ProcessRegistryTest(BaseModelMixin, TestCase):
    def test_register_function(self):
        registry = ProcessRegistry()
        self.assertEqual([], list(registry.keys()))
        self.assertEqual(None, registry.get("f1"))

        registry.register_function(f1)
        self.assertEqual(1, len(registry))
        p1 = list(registry.values())[0]
        self.assertIsInstance(p1, Process)
        self.assertIs(p1, registry.get(p1.description.id))

        registry.register_function(f2)
        self.assertEqual(2, len(registry))
        p1, p2 = registry.values()
        self.assertIsInstance(p1, Process)
        self.assertIsInstance(p2, Process)
        self.assertIs(p1, registry.get(p1.description.id))
        self.assertIs(p2, registry.get(p2.description.id))

    def test_to_json_dict(self):
        self.maxDiff = None
        registry = ProcessRegistry()
        registry.register_function(f1)
        registry.register_function(f2)
        registry.register_function(f3)

        json_dict = registry.to_json_dict()
        self.assertEqual(
            {
                "tests.process.test_process:f1",
                "tests.process.test_process:f2",
                "tests.process.test_process:f3",
            },
            set(json_dict.keys()),
        )
        self.assertEqual(
            "tests.process.test_process:f1",
            json_dict["tests.process.test_process:f1"].get("id"),
        )

        registry = ProcessRegistry()
        registry.register_function(f1, id="F1")
        registry.register_function(f2, id="F2")
        registry.register_function(f3, id="F3")
        json_dict = registry.to_json_dict()
        self.assertEqual({"F1", "F2", "F3"}, set(json_dict.keys()))
        self.assertEqual(
            "F1",
            json_dict["F1"].get("id"),
        )
