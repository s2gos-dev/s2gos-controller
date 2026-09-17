#  Copyright (c) 2025-2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from pathlib import Path
from unittest.mock import patch

import pytest
import s2gos_client.api
from cuiman.api import ClientConfig
from cuiman.api.auth import OAuth2AuthConfig
from s2gos_client.api import S2GOSConfig

MISSING_PROFILE = "/nonexistent/s2gos-client-profile"


def test_api_exports_ok():
    assert {
        "AsyncClient",
        "Client",
        "ClientConfig",
        "S2GOSConfig",
        "create_client",
        "create_async_client",
    }.issubset(dir(s2gos_client.api))


def test_create_client_selects_the_s2gos_namespace():
    with patch.object(s2gos_client.api, "Client") as client_type:
        client = s2gos_client.api.create_client(api_url="https://example.test")

    client_type.assert_called_once_with(
        config_type=S2GOSConfig, _debug=False, api_url="https://example.test"
    )
    assert client is client_type.return_value


def test_create_async_client_selects_the_s2gos_namespace():
    with patch.object(s2gos_client.api, "AsyncClient") as client_type:
        client = s2gos_client.api.create_async_client(api_url="https://example.test")

    client_type.assert_called_once_with(
        config_type=S2GOSConfig, _debug=False, api_url="https://example.test"
    )
    assert client is client_type.return_value


def test_s2gos_defaults_are_field_defaults():
    config = S2GOSConfig.create(config_path=MISSING_PROFILE)

    assert config.api_url == "https://s2gos.wraptile.brockmann-consult.de/"
    assert isinstance(config.auth, OAuth2AuthConfig)
    assert config.auth.auth_type == "oauth2"
    assert config.auth.grant_type == "password"
    assert config.auth.client_id == "cuiman"
    assert str(config.auth.token_url) == (
        "https://kc.dev.brockmann-consult.de/realms/dte-s2gos/protocol"
        "/openid-connect/token"
    )
    # Credentials are never baked into the application defaults.
    assert config.auth.username is None
    assert config.auth.password is None


def test_importing_s2gos_does_not_change_plain_cuiman():
    """The old `ClientConfig.default_config` assignment did exactly this."""
    assert ClientConfig.default_path == Path("~").expanduser() / ".eozilla" / "config"
    assert S2GOSConfig.default_path == Path("~").expanduser() / ".s2gos-client"

    plain = ClientConfig.create(config_path=MISSING_PROFILE)
    assert plain.api_url != S2GOSConfig.create(config_path=MISSING_PROFILE).api_url
    assert plain.auth.auth_type == "none"


def test_environment_namespaces_are_isolated(monkeypatch):
    monkeypatch.setenv("S2GOS_API_URL", "https://s2gos.test/")
    monkeypatch.setenv("EOZILLA_API_URL", "https://other.test/")

    assert S2GOSConfig.create(config_path=MISSING_PROFILE).api_url == "https://s2gos.test/"
    assert ClientConfig.create(config_path=MISSING_PROFILE).api_url == "https://other.test/"


def test_nested_auth_credentials_come_from_the_environment(monkeypatch):
    monkeypatch.setenv("S2GOS_AUTH__USERNAME", "tejas")
    monkeypatch.setenv("S2GOS_AUTH__PASSWORD", "secret")

    config = S2GOSConfig.create(config_path=MISSING_PROFILE)

    # A partial auth override merges into the application default rather
    # than replacing the provider settings it does not mention.
    assert config.auth.username == "tejas"
    assert config.auth.password == "secret"
    assert config.auth.client_id == "cuiman"


def test_s2gos_schema_allows_extra_settings_but_plain_cuiman_does_not():
    assert S2GOSConfig.create(config_path=MISSING_PROFILE, tenant="eu").tenant == "eu"
    with pytest.raises(ValueError):
        ClientConfig.create(config_path=MISSING_PROFILE, tenant="eu")


def test_a_resolved_config_keeps_its_namespace_when_rewrapped():
    """This is what `show_app()` does when it builds its backend client."""
    config = S2GOSConfig.create(config_path=MISSING_PROFILE)
    rewrapped = ClientConfig.create(config=config)

    assert type(rewrapped) is S2GOSConfig
    assert rewrapped.api_url == config.api_url
