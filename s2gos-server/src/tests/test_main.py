#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import importlib
from unittest import TestCase

import pytest
from fastapi import FastAPI
from tests.helpers import set_env_cm

from s2gos_server.provider import ServiceProvider
from s2gos_server.services.local.testing import service as test_service


class MainTest(TestCase):
    def setUp(self):
        ServiceProvider._service = None

    # noinspection PyMethodMayBeStatic
    def test_service_provider_init_ok(self):
        with set_env_cm(S2GOS_SERVICE="s2gos_server.services.local.testing:service"):
            module = importlib.import_module("s2gos_server.main")
            self.assertTrue(hasattr(module, "app"))
            self.assertIsInstance(getattr(module, "app"), FastAPI)
            service = ServiceProvider.get_instance()
            self.assertIsNotNone(service)
            self.assertIs(test_service, service)

    # noinspection PyMethodMayBeStatic
    def test_service_provider_init_fail(self):
        with pytest.raises(
            RuntimeError,
            match=(
                "Service not specified. "
                "Please set environment variable 'S2GOS_SERVICE'."
            ),
        ):
            with set_env_cm(S2GOS_SERVICE=None):
                ServiceProvider.get_instance()
