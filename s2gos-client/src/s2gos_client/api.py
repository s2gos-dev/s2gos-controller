#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from pathlib import Path

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


def create_config(username: str, password: str) -> ClientConfig:
    auth_config = AuthConfig(
        auth_url=_CONFIG_BASE.auth_url,
        auth_type="login",
        username=username,
        password=password,
    )
    token = login(auth_config)
    config_dict = _CONFIG_BASE.model_dump()
    config_dict.update(
        auth_type="token",
        token=token,
    )
    return S2GOSConfig(**config_dict)


def create_client(username: str, password: str) -> Client:
    return Client(config=create_config(username, password), _debug=_DEBUG)


def create_async_client(username: str, password: str) -> AsyncClient:
    return AsyncClient(config=create_config(username, password), _debug=_DEBUG)


__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "ClientError",
    "create_client",
    "create_async_client",
]
