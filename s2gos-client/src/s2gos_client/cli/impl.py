#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
from pathlib import Path

import click
import pydantic
import json
import yaml
from pydantic import BaseModel, Field

from s2gos_client import Client
from s2gos_client.api.config import ClientConfig
from s2gos_client.api.defaults import DEFAULT_SERVER_URL
from s2gos_common.models import ProcessRequest


class Request(BaseModel):
    process_id: str = Field(title="Process identifier", min_length=1)
    request: ProcessRequest = Field(title="Process request")


def configure_client(
    user_name: str | None = None,
    access_token: str | None = None,
    server_url: str | None = None,
):
    config = ClientConfig.read()
    if not user_name:
        user_name = click.prompt(
            "User name",
            default=(config and config.user_name)
            or os.environ.get("USER", os.environ.get("USERNAME")),
        )
    if not access_token:
        prev_access_token = config and config.access_token
        _access_token = click.prompt(
            "Access token",
            type=str,
            hide_input=True,
            default="*****" if prev_access_token else None,
        )
        if _access_token == "*****" and prev_access_token:
            access_token = prev_access_token
        else:
            access_token = _access_token
    if not server_url:
        server_url = click.prompt(
            "Server URL",
            default=(config and config.server_url) or DEFAULT_SERVER_URL,
        )
    config_path = ClientConfig(
        user_name=user_name, access_token=access_token, server_url=server_url
    ).write()
    click.echo(f"Configuration written to {config_path}")


def get_client(config_path: Path | str | None = None) -> Client:
    config = read_config(config_path=config_path)
    return Client(config=config)


def read_config(config_path: Path | str | None = None) -> ClientConfig:
    config = ClientConfig.read(config_path)
    if config is None:
        raise click.ClickException(
            "Tool is not yet configured,"
            " please use the 'configure' command to set it up."
        )
    return config


def read_request(request_path: Path | str):
    path = Path(request_path)
    with path.open("rt") as stream:
        if path.suffix in (".json", ".JSON"):
            request_dict = json.load(stream)
        else:
            request_dict = yaml.load(stream, Loader=yaml.SafeLoader)
    try:
        return Request(**request_dict)
    except pydantic.ValidationError as e:
        raise click.ClickException(f"Request {request_path} is invalid: {e}")
