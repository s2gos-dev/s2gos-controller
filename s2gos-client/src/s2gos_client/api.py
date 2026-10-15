#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
from pathlib import Path
from typing import Any

from cuiman.api import AsyncClient, Client, ClientConfig, ClientError
from cuiman.api.auth import AuthConfig, OAuth2AuthConfig
from cuiman.api.branding import AppBranding, AppImageIcon
from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict

_BRANDING_DIR = Path(__file__).resolve().parent / "app" / "branding"


class S2GOSConfig(ClientConfig):
    model_config = SettingsConfigDict(
        env_prefix="S2GOS_",
        env_file=".env",
        extra="allow",  # ClientConfig uses "forbid"
    )

    default_path = Path("~").expanduser() / ".s2gos-client"

    display_name = "S2GOS Client"
    cli_name = "s2gos-client"

    api_url: str | None = "https://s2gos-free.wraptile.brockmann-consult.de/"
    auth: AuthConfig = OAuth2AuthConfig(
        token_url=HttpUrl(
            "https://kc.dev.brockmann-consult.de/realms/dte-s2gos/protocol"
            "/openid-connect/token"
        ),
        client_id="cuiman",
        grant_type="password",
    )

    branding: AppBranding = AppBranding(
        title="S2GOS App",
        favicon=Path(_BRANDING_DIR / "favicon.ico"),
        icon=AppImageIcon(path=_BRANDING_DIR / "icon.png"),
    )


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
    return Client(config_type=S2GOSConfig, **config)


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
    return AsyncClient(config_type=S2GOSConfig, **config)


__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "ClientError",
    "S2GOSConfig",
    "create_client",
    "create_async_client",
]
