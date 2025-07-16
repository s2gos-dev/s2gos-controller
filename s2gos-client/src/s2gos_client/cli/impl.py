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
from s2gos_common.models import (
    ProcessRequest,
    JobInfo,
    JobList,
    JobResults,
    ProcessDescription,
    ProcessList,
)


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
    return Client(config)


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


def render_process_list(process_list: ProcessList):
    if not process_list.processes:
        click.echo(f"No processes available.")
    else:
        for i, process in enumerate(process_list.processes):
            click.echo(f"{i + 1}: {process.id} - {process.title}")


def render_process_description(process_description: ProcessDescription):
    click.echo(f"{process_description.id} - {process_description.title}:")
    if process_description.description:
        click.echo("")
        click.echo("Description")
        click.echo("-----------")
        click.echo(process_description.description)
    if process_description.inputs:
        click.echo("")
        click.echo("Inputs")
        click.echo("------")
    if process_description.outputs:
        click.echo("")
        click.echo("Outputs")
        click.echo("------")


def render_job_list(job_list: JobList):
    if not job_list.jobs:
        click.echo(f"No jobs available.")
    else:
        for i, job in enumerate(job_list.jobs):
            click.echo(
                f"{i + 1}: {job.id} - {job.status} - {job.progress} - {job.message}"
            )


def render_job(job: JobInfo):
    click.echo(f"Job ID:      {job.jobID}")
    click.echo(f"Process ID:  {job.processID}")
    click.echo(f"Status:      {job.status}")
    click.echo(f"Progress:    {job.progress}")
    click.echo(f"Message:     {job.message}")
    click.echo(f"Created at:  {job.created}")
    click.echo(f"Started at:  {job.started}")
    click.echo(f"Updated at:  {job.updated}")
    click.echo(f"Ended at:    {job.finished}")


def render_job_results(job_results: JobResults):
    results = job_results.model_dump_json(by_alias=True)
    click.echo(results)
