#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import ABC, abstractmethod
from io import StringIO
from typing import Literal

import click

import pydantic

from s2gos_common.models import (
    ProcessRequest,
    JobInfo,
    JobList,
    JobResults,
    ProcessDescription,
    ProcessList,
)
from .defaults import OutputFormat


class OutputRenderer(ABC):
    @classmethod
    def get(cls, output_format: OutputFormat) -> "OutputRenderer":
        return {
            OutputFormat.simple: SimpleOutputRenderer,
            OutputFormat.json: JsonOutputRenderer,
            OutputFormat.yaml: YamlOutputRenderer,
        }[output_format]()

    @abstractmethod
    def render_process_list(self, process_list: ProcessList):
        """Render a process list."""

    @abstractmethod
    def render_process_description(self, process_description: ProcessDescription):
        """Render a process description."""

    def render_process_request(self, process_request: ProcessRequest):
        """Render a process request."""

    @abstractmethod
    def render_job_list(self, job_list: JobList):
        """Render a job list."""

    @abstractmethod
    def render_job(self, job: JobInfo):
        """Render a job."""

    @abstractmethod
    def render_job_results(self, job_results: JobResults):
        """Render a job results."""

    @classmethod
    def _render_as_yaml(cls, base_model: pydantic.BaseModel):
        import yaml

        io = StringIO()
        with io as stream:
            yaml.safe_dump(
                OutputRenderer._model_to_dict(base_model), stream=stream, indent=2
            )
        click.echo(io.getvalue())

    @classmethod
    def _render_as_json(cls, base_model: pydantic.BaseModel):
        import yaml

        io = StringIO()
        with io as stream:
            yaml.safe_dump(
                OutputRenderer._model_to_dict(base_model), stream=stream, indent=2
            )
        click.echo(io.getvalue())

    @classmethod
    def _model_to_dict(cls, base_model: pydantic.BaseModel):
        return base_model.model_dump(
            mode="json",
            by_alias=True,
            exclude_defaults=True,
            exclude_none=True,
            exclude_unset=True,
        )


class SimpleOutputRenderer(OutputRenderer):
    def render_process_list(self, process_list: ProcessList):
        if not process_list.processes:
            click.echo("No processes available.")
        else:
            for i, process in enumerate(process_list.processes):
                click.echo(f"{i + 1}: {process.id} - {process.title}")

    def render_process_description(self, process_description: ProcessDescription):
        self._render_as_yaml(process_description)

    def render_process_request(self, process_request: ProcessRequest):
        self._render_as_yaml(process_request)

    def render_job_list(self, job_list: JobList):
        if not job_list.jobs:
            click.echo("No jobs available.")
        else:
            for i, job in enumerate(job_list.jobs):
                click.echo(
                    f"{i + 1}: {job.jobID} "
                    f"- {job.status} "
                    f"- {job.progress} "
                    f"- {job.message}"
                )

    def render_job(self, job: JobInfo):
        click.echo(f"Job ID:      {job.jobID}")
        click.echo(f"Process ID:  {job.processID}")
        click.echo(f"Status:      {job.status}")
        click.echo(f"Progress:    {job.progress}")
        click.echo(f"Message:     {job.message}")
        click.echo(f"Created at:  {job.created}")
        click.echo(f"Started at:  {job.started}")
        click.echo(f"Updated at:  {job.updated}")
        click.echo(f"Ended at:    {job.finished}")

    def render_job_results(self, job_results: JobResults):
        self._render_as_yaml(job_results)


class StructuredOutputRenderer(OutputRenderer):
    def __init__(self, fmt: Literal["json", "yaml"]):
        self.fmt = fmt

    def _render_base_model(self, base_model: pydantic.BaseModel):
        io = StringIO()
        with io as stream:
            if self.fmt == "yaml":
                import yaml

                yaml.safe_dump(self._model_to_dict(base_model), stream, indent=2)
            else:
                import json

                json.dump(self._model_to_dict(base_model), stream, indent=2)

        click.echo(io.getvalue())

    def render_process_list(self, process_list: ProcessList):
        self._render_base_model(process_list)

    def render_process_description(self, process_description: ProcessDescription):
        self._render_base_model(process_description)

    def render_process_request(self, process_request: ProcessRequest):
        self._render_base_model(process_request)

    def render_job_list(self, job_list: JobList):
        self._render_base_model(job_list)

    def render_job(self, job: JobInfo):
        self._render_base_model(job)

    def render_job_results(self, job_results: JobResults):
        self._render_as_yaml(job_results)


class YamlOutputRenderer(StructuredOutputRenderer):
    def __init__(self):
        super().__init__("yaml")


class JsonOutputRenderer(StructuredOutputRenderer):
    def __init__(self):
        super().__init__("json")
