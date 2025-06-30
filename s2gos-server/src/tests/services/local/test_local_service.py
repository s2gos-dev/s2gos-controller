#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos_common.models import ProcessDescription
from s2gos_server.services.local import LocalService, ProcessRegistry


class LocalServiceTest(TestCase):
    def test_process_registration(self):
        service = LocalService(title="OGC API - Processes - Test Service")

        self.assertIsNone(service.process_registry.get_entry("foo"))
        self.assertIsNone(service.process_registry.get_entry("bar"))

        def foo(x: bool, y: int) -> float:
            return 2 * y if x else y / 2

        service.register_process(foo, id="foo", version="1.0.0")

        @service.process(id="bar", version="1.4.2")
        def bar(x: bool, y: int) -> float:
            return 2 * y if x else y / 2

        foo_entry = service.process_registry.get_entry("foo")
        self.assertIsInstance(foo_entry, ProcessRegistry.Entry)
        self.assertIs(foo, foo_entry.function)
        foo_process = foo_entry.process
        self.assertIsInstance(foo_process, ProcessDescription)
        self.assertEqual("foo", foo_process.id)
        self.assertEqual("1.0.0", foo_process.version)

        bar_entry = service.process_registry.get_entry("bar")
        self.assertIsInstance(bar_entry, ProcessRegistry.Entry)
        self.assertIs(bar, bar_entry.function)
        bar_process = bar_entry.process
        self.assertIsInstance(bar_process, ProcessDescription)
        self.assertEqual("bar", bar_process.id)
        self.assertEqual("1.4.2", bar_process.version)
