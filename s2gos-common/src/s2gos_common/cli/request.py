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
    process_id: str | None = None,
    request_file: str | None = None,
    request_inputs: list[str] | None = None,
    request_subscribers: list[str] | None = None,
) -> ProcessingRequest:
    request_dict, request_file = read_processing_request_from_file(request_file)
    if process_id:
        request_dict["process_id"] = process_id
    inputs_dict = parse_request_inputs(request_inputs)
    if inputs_dict:
        request_dict["inputs"] = dict(request_dict.get("inputs") or {})
        request_dict["inputs"].update(inputs_dict)
    subscriber_dict = parse_request_subscribers(request_subscribers)
    if subscriber_dict:
        request_dict["subscriber"] = dict(request_dict.get("subscriber") or {})
        request_dict["subscriber"].update(subscriber_dict)
    try:
        return ProcessingRequest(**request_dict)
    except pydantic.ValidationError as e:
        raise click.ClickException(f"Processing request is invalid: {e}")


def read_processing_request_from_file(
    request_path: str | None = None,
) -> tuple[dict[str, Any], str]:
    if not request_path:
        return {}, ""

    if request_path == "-":
        request_path = "<stdin>"
        # content = "\n".join(line for line in sys.stdin).strip()
        content = sys.stdin.read().strip()
        file_format = "json" if content.startswith("{") else "yaml"
    else:
        path = Path(request_path)
        content = path.read_text()
        file_format = "json" if path.suffix in (".json", ".JSON") else "yaml"

    if file_format == "json":
        import json

        request_dict = json.loads(content)
    else:
        import yaml

        request_dict = yaml.safe_load(StringIO(content))

    if not isinstance(request_dict, dict):
        raise click.ClickException(
            f"Request must be an object, but was type {type(request_dict).__name__}"
        )

    return request_dict, request_path


def parse_request_inputs(request_inputs: list[str] | None) -> dict[str, Any]:
    import json

    inputs_dict: dict[str, Any] = {}
    for name, value in _parse_kv_list(request_inputs, "request input"):
        try:
            json_value = json.loads(value)
        except json.JSONDecodeError:
            json_value = value
        inputs_dict[name] = json_value
    return inputs_dict


def parse_request_subscribers(request_subscribers: list[str] | None) -> dict[str, Any]:
    return _parse_kv_list(request_subscribers, "request subscriber")


def _parse_kv_list(kv_list: list[str] | None, item_name: str) -> dict[str, Any]:
    d: dict[str, Any] = {}
    for kv in kv_list or []:
        try:
            k, v = kv.split("=", maxsplit=1)
        except ValueError:
            raise click.ClickException(f"Invalid {item_name}: {kv}")
        d[k] = v
    return d
