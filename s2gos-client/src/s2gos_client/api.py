#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from pathlib import Path
from typing import Any

from cuiman.api import AsyncClient, Client, ClientConfig, ClientError
from cuiman.api.auth import AuthConfig, login
from pydantic_settings import SettingsConfigDict


class S2GOSConfig(ClientConfig):
    model_config = SettingsConfigDict(
        env_prefix="S2GOS_",
        env_file=".env",
        extra="allow",  # ClientConfig uses "forbid"
    )


_CONFIG_BASE = S2GOSConfig(
    api_url="http://localhost:8008/",
    auth_url=None,
    auth_type="none",
)
_DEBUG = False

ClientConfig.default_path = Path("~").expanduser() / ".s2gos-client"
ClientConfig.default_config = _CONFIG_BASE


def _create_config(**config_overrides: Any) -> ClientConfig:
    """
    Create the S2GOS-specific configuration instance
    from given configuration overrides.
    """
    config_dict = _CONFIG_BASE.model_dump()
    config_dict.update(config_overrides)

    auth_config_dict = dict(config_dict)
    auth_config_dict.pop("api_url", None)

    auth_config = AuthConfig(**auth_config_dict)
    if auth_config.auth_type == "login":
        token = login(auth_config)
        config_dict.update(
            auth_type="token",
            token=token,
        )

    return S2GOSConfig(**config_dict)


def create_client(**config: Any) -> Client:
    """Create a synchronous S2GOS client from given configuration.

    Provided configuration values, if any, override values
    read from persistent configuration that were previously
    written by the CLI command `s2gos-controller configure`.

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
    written by the CLI command `s2gos-controller configure`.

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
