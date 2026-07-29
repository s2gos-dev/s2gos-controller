#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from pathlib import Path
from typing import Any

from cuiman.api import AsyncClient, Client, ClientConfig, ClientError
from cuiman.api.auth import login_for_tokens
from pydantic_settings import SettingsConfigDict


class S2GOSConfig(ClientConfig):
    model_config = SettingsConfigDict(
        env_prefix="S2GOS_",
        env_file=".env",
        extra="allow",  # ClientConfig uses "forbid"
    )


_CONFIG_BASE = S2GOSConfig(
    api_url="https://s2gos.wraptile.brockmann-consult.de/",
    auth_type="login",
    auth_url=(
        "https://kc.dev.brockmann-consult.de/realms/eozilla-auth/protocol"
        "/openid-connect/token"
    ),
    client_id="cuiman",
    grant_type="password",
    use_bearer=True,
)
_DEBUG = False

ClientConfig.default_path = Path("~").expanduser() / ".s2gos-client"
ClientConfig.default_config = _CONFIG_BASE


def _create_config(**config_overrides: Any) -> ClientConfig:
    """
    Create the S2GOS-specific configuration instance
    from given configuration overrides.
    """
    config = S2GOSConfig.create(**config_overrides)
    if config.auth_type != "login":
        return config

    # Always obtain fresh tokens: a token read from persistent configuration is
    # likely expired, and so is its refresh token. Authentication stays of type
    # "login", which lets the underlying transport refresh the access token
    # after a 401 response.
    result = login_for_tokens(config)
    config.token = result.access_token
    config.refresh_token = result.refresh_token
    return config


def create_client(**config: Any) -> Client:
    """Create a synchronous S2GOS client from given configuration.

    Provided configuration values, if any, override values
    read from persistent configuration that were previously
    written by the CLI command `s2gos-client configure`.

    Args:
        config: Configuration overrides. See
            https://eo-tools.github.io/eozilla/cuiman/configuration/
            for details.
    Returns:
        An instance of a synchronous cuiman client for S2GOS. See
        https://eo-tools.github.io/eozilla/cuiman/ for details.
    """
    return Client(config=_create_config(**config), _debug=_DEBUG)


def create_async_client(**config: Any) -> AsyncClient:
    """Create an asynchronous S2GOS client from given configuration.

    Provided configuration values, if any, override values
    read from persistent configuration that were previously
    written by the CLI command `s2gos-client configure`.

    Args:
        config: Configuration overrides. See
            https://eo-tools.github.io/eozilla/cuiman/configuration/
            for details.
    Returns:
        An instance of an asynchronous cuiman client for S2GOS. See
        https://eo-tools.github.io/eozilla/cuiman/ for details.
    """
    return AsyncClient(config=_create_config(**config), _debug=_DEBUG)


__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "ClientError",
    "create_client",
    "create_async_client",
]
