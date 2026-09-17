#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
from importlib.resources import files
from pathlib import Path
from typing import Any, ClassVar

from cuiman.api import AsyncClient, Client, ClientConfig, ClientError
from cuiman.api.auth import AuthConfig, OAuth2AuthConfig
from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict

_DEBUG = False


class S2GOSConfig(ClientConfig):
    """Configuration namespace of the S2GOS client.

    This class owns the S2GOS settings schema, its field defaults, its
    `S2GOS_` environment namespace, and its persistent profile location.
    Importing this module therefore leaves plain `cuiman` and any other
    `cuiman`-based application unchanged.
    """

    model_config = SettingsConfigDict(
        env_prefix="S2GOS_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="allow",  # base ClientConfig uses "forbid"
    )

    default_path: ClassVar[Path] = Path("~").expanduser() / ".s2gos-client"

    api_url: str | None = "https://s2gos.wraptile.brockmann-consult.de/"

    auth: AuthConfig = OAuth2AuthConfig(
        token_url=HttpUrl(
            "https://kc.dev.brockmann-consult.de/realms/dte-s2gos/protocol"
            "/openid-connect/token"
        ),
        client_id="cuiman",
        grant_type="password",
    )


# Default show_app() to the S2GOS-branded GUI build bundled with this
# package, unless the user has already set EOZILLA_APP_DIST themselves
# (e.g. to point at a local frontend dev build).
os.environ.setdefault(
    "EOZILLA_APP_DIST", str(files("s2gos_client.app").joinpath("dist"))
)


def create_client(**config: Any) -> Client:
    """Create a synchronous S2GOS client from given configuration.

    Provided configuration values, if any, override values read from the
    `S2GOS_` environment namespace and from the persistent configuration
    that was previously written by the CLI command `s2gos-client configure`.

    The client is not logged in on return. It authenticates with the
    available credentials before its first request; call `client.login()`
    explicitly when the credentials must be prompted for or refreshed.

    Args:
        config: Configuration overrides. See
            https://eo-tools.github.io/eozilla/cuiman/configuration/
            for details.
    Returns:
        An instance of a synchronous cuiman client for S2GOS. See
        https://eo-tools.github.io/eozilla/cuiman/ for details.
    """
    return Client(config_type=S2GOSConfig, _debug=_DEBUG, **config)


def create_async_client(**config: Any) -> AsyncClient:
    """Create an asynchronous S2GOS client from given configuration.

    Provided configuration values, if any, override values read from the
    `S2GOS_` environment namespace and from the persistent configuration
    that was previously written by the CLI command `s2gos-client configure`.

    The client is not logged in on return. It authenticates with the
    available credentials before its first request; call `await
    client.login()` explicitly when the credentials must be prompted for
    or refreshed.

    Args:
        config: Configuration overrides. See
            https://eo-tools.github.io/eozilla/cuiman/configuration/
            for details.
    Returns:
        An instance of an asynchronous cuiman client for S2GOS. See
        https://eo-tools.github.io/eozilla/cuiman/ for details.
    """
    return AsyncClient(config_type=S2GOSConfig, _debug=_DEBUG, **config)


__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "ClientError",
    "S2GOSConfig",
    "create_client",
    "create_async_client",
]
