#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import ABC, abstractmethod
from enum import Enum
from io import StringIO
from typing import Literal

import pydantic
import typer

from s2gos_common.models import (
    JobInfo,
    JobList,
    JobResults,
    ProcessDescription,
    ProcessList,
)

from .request import ProcessingRequest


class OutputFormat(str, Enum):
    simple = "simple"
    json = "json"
    yaml = "yaml"


def get_renderer(
    output_format: OutputFormat, verbose: bool = False
) -> "OutputRenderer":
    return {
        OutputFormat.simple: SimpleOutputRenderer,
        OutputFormat.json: JsonOutputRenderer,
        OutputFormat.yaml: YamlOutputRenderer,
    }[output_format](verbose)


class OutputRenderer(ABC):
    @abstractmethod
    def render_process_list(self, process_list: ProcessList):
        """Render a process list."""

    @abstractmethod
    def render_process_description(self, process_description: ProcessDescription):
        """Render a process description."""

    def render_processing_request(self, process_request: ProcessingRequest):
        """Render a processing request."""

    def render_processing_request_valid(self, process_request: ProcessingRequest):
        """Render a processing request is valid."""

    @abstractmethod
    def render_job_list(self, job_list: JobList):
        """Render a job list."""

    @abstractmethod
    def render_job(self, job: JobInfo):
        """Render a job."""

    @abstractmethod
    def render_job_results(self, job_results: JobResults):
        """Render a job results."""

    def _render_base_model(
        self,
        base_model: pydantic.BaseModel,
        format_name: Literal["json", "yaml"] = "yaml",
    ):
        serialized_value = self._serialize_model(base_model)
        if format_name == "yaml":
            import yaml

            text_value = yaml.safe_dump(serialized_value, indent=2)
        else:
            import json

            text_value = json.dumps(serialized_value, indent=2)
        typer.echo(text_value)

    @classmethod
    def _serialize_model(cls, base_model: pydantic.BaseModel):
        return base_model.model_dump(
            mode="json",
            by_alias=True,
            exclude_defaults=True,
            exclude_none=True,
            exclude_unset=True,
        )


class SimpleOutputRenderer(OutputRenderer):
    def __init__(self, verbose: bool):
        self.verbose = verbose

    def render_process_list(self, process_list: ProcessList):
        if not process_list.processes:
            typer.echo("No processes available.")
        else:
            for i, process in enumerate(process_list.processes):
                typer.echo(f"{i + 1}: {process.id} - {process.title}")

    def render_process_description(self, process_description: ProcessDescription):
        self._render_base_model(process_description)

    def render_processing_request(self, processing_request: ProcessingRequest):
        self._render_base_model(processing_request)

    def render_processing_request_valid(self, processing_request: ProcessingRequest):
        typer.echo("Processing request is valid:")
        self._render_base_model(processing_request)

    def render_job_list(self, job_list: JobList):
        if not job_list.jobs:
            typer.echo("No jobs available.")
        else:
            for i, job in enumerate(job_list.jobs):
                typer.echo(
                    f"{i + 1}: {job.jobID} "
                    f"- {job.status} "
                    f"- {job.progress} "
                    f"- {job.message}"
                )

    def render_job(self, job: JobInfo):
        typer.echo(f"Job ID:      {job.jobID}")
        typer.echo(f"Process ID:  {job.processID}")
        typer.echo(f"Status:      {job.status}")
        typer.echo(f"Progress:    {job.progress}")
        typer.echo(f"Message:     {job.message}")
        typer.echo(f"Created at:  {job.created}")
        typer.echo(f"Started at:  {job.started}")
        typer.echo(f"Updated at:  {job.updated}")
        typer.echo(f"Ended at:    {job.finished}")

    def render_job_results(self, job_results: JobResults):
        self._render_base_model(job_results)


class StructuredOutputRenderer(OutputRenderer):
    def __init__(self, format_name: Literal["json", "yaml"], verbose: bool):
        self.format_name = format_name
        self.verbose = verbose

    def render_process_list(self, process_list: ProcessList):
        self._render_base_model(process_list, self.format_name)

    def render_process_description(self, process_description: ProcessDescription):
        self._render_base_model(process_description, self.format_name)

    def render_processing_request(self, processing_request: ProcessingRequest):
        self._render_base_model(processing_request, self.format_name)

    def render_processing_request_valid(self, processing_request: ProcessingRequest):
        self._render_base_model(processing_request, self.format_name)

    def render_job_list(self, job_list: JobList):
        self._render_base_model(job_list, self.format_name)

    def render_job(self, job: JobInfo):
        self._render_base_model(job, self.format_name)

    def render_job_results(self, job_results: JobResults):
        self._render_base_model(job_results, self.format_name)


class YamlOutputRenderer(StructuredOutputRenderer):
    def __init__(self, verbose: bool):
        super().__init__("yaml", verbose)


class JsonOutputRenderer(StructuredOutputRenderer):
    def __init__(self, verbose: bool):
        super().__init__("json", verbose)
