#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel

from .defaults import DEFAULT_CONFIG_PATH


class ClientConfig(BaseModel):
    """Client configuration.

    Args:
        user_name: name of the registered S2GOS user
        access_token: API access token
        server_url: server API URL
    """

    user_name: Optional[str] = None
    access_token: Optional[str] = None
    server_url: Optional[str] = None

    def _repr_json_(self):
        return self.model_dump(mode="json", by_alias=True), dict(root="Configuration:")

    @classmethod
    def read(cls, config_path: Optional[str | Path] = None) -> Optional["ClientConfig"]:
        config_path = cls.normalize_config_path(config_path)

        default_config_dict = {}
        for field_name, _field_info in ClientConfig.model_fields.items():
            env_var_name = "S2GOS_" + field_name.upper()
            if env_var_name in os.environ:
                default_config_dict[field_name] = os.environ[env_var_name]

        config_dict = {}
        if not config_path.exists():
            config_dict = default_config_dict
        else:
            with config_path.open("rt") as stream:
                config_dict = yaml.load(stream, Loader=yaml.SafeLoader)
                for k, v in default_config_dict.items():
                    if k not in config_dict:
                        config_dict[k] = v
        return ClientConfig.model_validate(config_dict)

    def write(self, config_path: Optional[str | Path] = None) -> Path:
        config_path = self.normalize_config_path(config_path)
        config_path.parent.mkdir(exist_ok=True)
        with config_path.open("wt") as stream:
            yaml.dump(
                self.model_dump(mode="json", by_alias=True, exclude_none=True), stream
            )
        return config_path

    @classmethod
    def normalize_config_path(cls, config_path) -> Path:
        if isinstance(config_path, Path):
            return config_path
        if not config_path:
            return DEFAULT_CONFIG_PATH
        return Path(config_path)
