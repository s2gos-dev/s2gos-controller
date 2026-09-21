#  Copyright (c) 2025-2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os

import pytest
from cuiman.api.auth import NoAuthConfig, OAuth2AuthConfig, TokenAuthConfig

import s2gos_client.api as api


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(api.S2GOSConfig, "default_path", tmp_path / "config.yaml")
    for name in os.environ:
        if name.upper().startswith(("S2GOS_", "EOZILLA_")):
            monkeypatch.delenv(name)


@pytest.fixture(params=[api.create_client, api.create_async_client], ids=["sync", "async"])
def create_client(request):
    return request.param


def test_api_exports_ok():
    assert {
        "AsyncClient",
        "Client",
        "ClientConfig",
        "ClientError",
        "create_client",
        "create_async_client",
    }.issubset(dir(api))


def test_create_client_uses_s2gos_defaults(create_client):
    client = create_client()

    client_type = api.Client if create_client is api.create_client else api.AsyncClient
    assert isinstance(client, client_type)
    assert isinstance(client.config, api.S2GOSConfig)
    assert client.config.api_url == "https://s2gos.wraptile.brockmann-consult.de/"
    auth = client.config.auth
    assert isinstance(auth, OAuth2AuthConfig)
    assert str(auth.token_url) == (
        "https://kc.dev.brockmann-consult.de/realms/dte-s2gos/protocol"
        "/openid-connect/token"
    )
    assert auth.client_id == "cuiman"
    assert auth.grant_type == "password"


def test_create_client_accepts_auth_override(create_client):
    client = create_client(
        api_url="https://example.test/",
        auth={"auth_type": "token", "access_token": "test-token"},
    )

    assert client.config.api_url == "https://example.test/"
    assert isinstance(client.config.auth, TokenAuthConfig)
    assert client.config.auth.access_token == "test-token"


def test_create_client_overrides_persisted_settings(create_client, tmp_path):
    config_path = tmp_path / "profile.yaml"
    config_path.write_text(
        "api_url: https://saved.test/\nauth:\n  auth_type: none\n",
        encoding="utf-8",
    )

    saved = create_client(config_path=str(config_path))
    overridden = create_client(
        config_path=str(config_path), api_url="https://override.test/"
    )

    assert saved.config.api_url == "https://saved.test/"
    assert overridden.config.api_url == "https://override.test/"
    assert isinstance(overridden.config.auth, NoAuthConfig)


def test_create_client_uses_s2gos_environment(create_client, monkeypatch):
    monkeypatch.setenv("S2GOS_API_URL", "https://s2gos-env.test/")
    monkeypatch.setenv("EOZILLA_API_URL", "https://eozilla-env.test/")

    assert create_client().config.api_url == "https://s2gos-env.test/"
    assert create_client(api_url="https://explicit.test/").config.api_url == (
        "https://explicit.test/"
    )


def test_client_auth_defaults_are_independent(create_client):
    first = create_client()
    first.config.auth.client_id = "changed"

    assert create_client().config.auth.client_id == "cuiman"
