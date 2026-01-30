#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from pathlib import Path

from pydantic_settings import SettingsConfigDict

from cuiman.api import AsyncClient, Client, ClientConfig, ClientError


class S2GOSConfig(ClientConfig):
    model_config = SettingsConfigDict(
        env_prefix="S2GOS_",
        env_file=".env",
        extra="allow",  # ClientConfig uses "forbid"
    )


ClientConfig.default_path = Path("~").expanduser() / ".sen4cap-client"
ClientConfig.default_config = S2GOSConfig(
    api_url="http://localhost:8008/",
    # auth_url="http://localhost:8080/auth/login",
    # auth_type="token",
    # use_bearer=True,
    auth_type="none",
)

__all__ = [
    "AsyncClient",
    "Client",
    "ClientConfig",
    "ClientError",
]
