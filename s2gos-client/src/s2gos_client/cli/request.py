#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import sys
from io import StringIO
from pathlib import Path
from typing import Any

import click
import pydantic
from pydantic import Field

from s2gos_common.models import ProcessRequest


class ProcessingRequest(ProcessRequest):
    process_id: str = Field(title="Process identifier", min_length=1)

    def as_process_request(self) -> ProcessRequest:
        return ProcessRequest(
            inputs=self.inputs,
            outputs=self.outputs,
            response=self.response,
            subscriber=self.subscriber,
        )


def read_processing_request(
    process_id: str | None,
    parameters: list[str] | None,
    request_file: str | None,
) -> ProcessingRequest:
    if request_file and process_id:
        raise click.ClickException(
            "The `--request` option and the `process_id` "
            "argument are mutually exclusive."
        )
    if process_id:
        return read_processing_request_from_args(process_id, parameters)
    else:
        return read_processing_request_from_file(request_file)


def read_processing_request_from_args(
    process_id: str,
    parameters: list[str] | None,
) -> ProcessingRequest:
    request_dict: dict[str, Any] = {"process_id": process_id}
    if parameters:
        import yaml

        inputs_dict: dict[str, Any] = {}
        for parameter in parameters:
            try:
                name, value = parameter.split("=", maxsplit=1)
                try:
                    data = yaml.safe_load(StringIO(f"{name}: {value}"))
                except yaml.YAMLError:
                    raise ValueError
                if not isinstance(data, dict) or len(data) != 1:
                    raise ValueError
            except ValueError:
                raise click.ClickException(f"Invalid parameter argument: {parameter}")
            name, value = next(iter(data.items()))
            inputs_dict[name] = value
        request_dict["inputs"] = inputs_dict
    return new_processing_request(
        request_dict, source="arguments" if parameters else "argument"
    )


def read_processing_request_from_file(
    request_path: str | None = None,
) -> ProcessingRequest:
    if request_path:
        path = Path(request_path)
        content = path.read_text()
        file_format = "json" if path.suffix in (".json", ".JSON") else "yaml"
    elif not sys.stdin.isatty():
        request_path = "<stdin>"
        content = "\n".join(line for line in sys.stdin).strip()
        file_format = "json" if content.startswith("{") else "yaml"
    else:
        raise click.ClickException("Missing processing request.")
    if file_format == "json":
        import json

        request_dict = json.loads(content)
    else:
        import yaml

        string_io = StringIO(content)
        request_dict = yaml.safe_load(string_io)
    return new_processing_request(request_dict, source=str(request_path))


def new_processing_request(
    request_dict: dict[str, Any], source: str
) -> ProcessingRequest:
    try:
        return ProcessingRequest(**request_dict)
    except pydantic.ValidationError as e:
        raise click.ClickException(f"Processing request from {source} is invalid: {e}")
