#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos_common.models import ProcessDescription
from s2gos_server.services.local import LocalService, ProcessRegistry


class LocalServiceTest(TestCase):
    @staticmethod
    def get_service() -> LocalService:
        return LocalService(title="OGC API - Processes - Test Service")

    def test_process_decorator(self):
        service = self.get_service()

        self.assertIsNone(service.process_registry.get_entry("foo"))

        @service.process(id="foo", version="1.4.2")
        def foo(x: bool, y: int) -> float:
            return 2 * y if x else y / 2

        entry = service.process_registry.get_entry("foo")
        self.assertIsInstance(entry, ProcessRegistry.Entry)
        self.assertIs(foo, entry.function)
        foo_process = entry.process
        self.assertIsInstance(foo_process, ProcessDescription)
        self.assertEqual("foo", foo_process.id)
        self.assertEqual("1.4.2", foo_process.version)
