#  Copyright (c) 2025-2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest.mock import Mock, patch

import s2gos_client.api
from cuiman.api.auth import LoginResult


def test_api_exports_ok():
    assert {
        "AsyncClient",
        "Client",
        "ClientConfig",
        "create_client",
        "create_async_client",
    }.issubset(dir(s2gos_client.api))


def test_create_client():
    config = Mock(auth_type="token")

    with (
        patch.object(
            s2gos_client.api.ClientConfig, "create", return_value=config
        ) as create_config,
        patch.object(s2gos_client.api, "Client") as client_type,
    ):
        client = s2gos_client.api.create_client(api_url="https://example.test")

    create_config.assert_called_once_with(api_url="https://example.test")
    client_type.assert_called_once_with(config=config, _debug=False)
    assert client is client_type.return_value


def test_create_async_client():
    config = Mock(auth_type="token")

    with (
        patch.object(
            s2gos_client.api.ClientConfig, "create", return_value=config
        ) as create_config,
        patch.object(s2gos_client.api, "AsyncClient") as client_type,
    ):
        client = s2gos_client.api.create_async_client(api_url="https://example.test")

    create_config.assert_called_once_with(api_url="https://example.test")
    client_type.assert_called_once_with(config=config, _debug=False)
    assert client is client_type.return_value


def test_create_config_logs_in_and_retains_refresh_token():
    config = Mock(auth_type="login", token=None)
    login_result = LoginResult(
        access_token="access-token",
        refresh_token="refresh-token",
    )

    with (
        patch.object(
            s2gos_client.api.ClientConfig, "create", return_value=config
        ) as create_config,
        patch.object(
            s2gos_client.api, "login_for_tokens", return_value=login_result
        ) as login,
    ):
        created_config = s2gos_client.api._create_config(api_url="https://example.test")

    create_config.assert_called_once_with(api_url="https://example.test")
    login.assert_called_once_with(config)
    assert created_config is config
    assert config.auth_type == "login"
    assert config.token == "access-token"
    assert config.refresh_token == "refresh-token"


def test_create_config_replaces_persisted_login_token():
    config = Mock(
        auth_type="login",
        token="old-access-token",
        refresh_token="old-refresh-token",
    )
    login_result = LoginResult(
        access_token="access-token",
        refresh_token="refresh-token",
    )

    with (
        patch.object(
            s2gos_client.api.ClientConfig, "create", return_value=config
        ) as create_config,
        patch.object(
            s2gos_client.api, "login_for_tokens", return_value=login_result
        ) as login,
    ):
        created_config = s2gos_client.api._create_config(api_url="https://example.test")

    create_config.assert_called_once_with(api_url="https://example.test")
    login.assert_called_once_with(config)
    assert created_config is config
    assert config.token == "access-token"
    assert config.refresh_token == "refresh-token"
