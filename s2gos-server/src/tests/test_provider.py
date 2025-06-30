#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos_server.provider import ServiceProvider, get_service
from s2gos_server.services.local import LocalService


class ServiceProviderTest(TestCase):
    def setUp(self):
        ServiceProvider._service = None

    def test_set_instance(self):
        service = LocalService(title="Test service")
        ServiceProvider.set_instance(service)
        self.assertIs(service, ServiceProvider.get_instance())
        self.assertIs(service, get_service())
