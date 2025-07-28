#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import pytest

from s2gos_common.testing import set_env_cm
from s2gos_server.constants import S2GOS_SERVICE_ENV_VAR
from s2gos_server.exceptions import ConfigException
from s2gos_server.services.base import ServiceBase


class ServiceBaseTest(TestCase):
    def test_load_env_var_not_set(self):
        self.assert_fails_with_config_exception(
            None, r"Service not specified\. The service must be passed in the form"
        )

    def test_load_env_var_empty(self):
        self.assert_fails_with_config_exception(
            "", r"Service not specified\. The service must be passed in the form"
        )

    def test_load_env_var_with_invalid_service_spec(self):
        self.assert_fails_with_config_exception(
            "hello.service",
            r"The service must be passed in the form "
            r"'path\.to\.module\:service', but got 'hello\.service'\.",
        )

    def test_load_env_var_with_invalid_service_module(self):
        self.assert_fails_with_config_exception(
            "hel.lo:service",
            r"Cannot import the service module 'hel.lo'\.",
        )

    def test_load_env_var_with_invalid_service_attrib(self):
        self.assert_fails_with_config_exception(
            "s2gos_server.services.local.testing:servize",
            r"Service module 's2gos_server\.services\.local\.testing' "
            r"has no attribute 'servize'\.",
        )

    def test_load_env_var_with_invalid_service_type(self):
        self.assert_fails_with_config_exception(
            "s2gos_server.services.local.testing:SceneSpec",
            r"'s2gos_server\.services\.local\.testing:SceneSpec' "
            r"is not referring to a service instance\.",
        )

    def test_load_env_var_with_invalid_opt(self):
        self.assert_fails_with_config_exception(
            "module:attr -pippo",
            r"Service options must have the form '\-\-key\[=value\]', "
            r"but got '-pippo'\.",
        )

    def test_load_env_var_with_invalid_opt_ident(self):
        self.assert_fails_with_config_exception(
            "module:attr --12=13",
            r"Service options must have the form '--key\[=value\]', "
            r"but got '12' as key, which is not an identifier\.",
        )

    # noinspection PyMethodMayBeStatic
    def assert_fails_with_config_exception(self, value: str | None, match: str):
        with set_env_cm(**{S2GOS_SERVICE_ENV_VAR: value}):
            with pytest.raises(ConfigException, match=match):
                ServiceBase.load()
