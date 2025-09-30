#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import sys
from io import StringIO
from pathlib import Path
from typing import Annotated, Any

import click
import pydantic
from pydantic import Field

from s2gos_common.models import ProcessRequest

SUBSCRIBER_EVENTS = {
    "success": "successUri",
    "failed": "failedUri",
    "progress": "inProgressUri",
}


class ProcessingRequest(ProcessRequest):
    process_id: Annotated[str, Field(title="Process identifier", min_length=1)]
    dotpath: Annotated[
        bool, Field(title="Whether to encode nested input values using dots ('.').")
    ] = False

    def as_process_request(self) -> ProcessRequest:
        inputs = self.inputs
        if inputs and self.dotpath:
            inputs = self._nest_dict(inputs)
        return ProcessRequest(
            inputs=inputs,
            outputs=self.outputs,
            response=self.response,
            subscriber=self.subscriber,
        )

    @classmethod
    def create(
        cls,
        process_id: str | None = None,
        dotpath: bool = False,
        request_path: str | None = None,
        inputs: list[str] | None = None,
        subscribers: list[str] | None = None,
    ) -> "ProcessingRequest":
        request_dict, _ = _read_processing_request(request_path)
        if process_id:
            request_dict["process_id"] = process_id
        if dotpath:
            request_dict["dotpath"] = dotpath
        inputs_dict = _parse_inputs(inputs)
        if inputs_dict:
            request_dict["inputs"] = dict(request_dict.get("inputs") or {})
            request_dict["inputs"].update(inputs_dict)
        subscriber_dict = _parse_subscribers(subscribers)
        if subscriber_dict:
            request_dict["subscriber"] = dict(request_dict.get("subscriber") or {})
            request_dict["subscriber"].update(subscriber_dict)
        try:
            return ProcessingRequest(**request_dict)
        except pydantic.ValidationError as e:
            raise click.ClickException(f"Processing request is invalid: {e}")

    @classmethod
    def _nest_dict(cls, flat_dict: dict[str, Any]) -> dict[str, Any]:
        nested_dict: dict[str, Any] = {}
        for key, value in flat_dict.items():
            path = key.split(".")
            current = nested_dict
            for name in path[:-1]:
                current = current.setdefault(name, {})
            current[path[-1]] = value
        return nested_dict


def _read_processing_request(
    request_path: Path | str | None = None,
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

    return request_dict, str(request_path)


def _parse_inputs(inputs: list[str] | None) -> dict[str, Any]:
    return dict(_parse_inputs_kv(kv) for kv in (inputs or []))


def _parse_inputs_kv(kv: str) -> tuple[str, str]:
    parts = kv.split("=", maxsplit=1)
    key, value = parts if len(parts) == 2 else (parts[0], "true")
    return _parse_input_name(key), _parse_input_value(value)


def _parse_input_name(key: str) -> str:
    norm_key = key.strip().replace("-", "_")

    property_names = key.split(".")
    for property_name in property_names:
        if not property_name.isidentifier():
            raise click.ClickException(f"Invalid request NAME: {key!r}")

    return norm_key


def _parse_input_value(value: str) -> Any:
    import json

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _parse_subscribers(subscribers: list[str] | None) -> dict[str, str]:
    return dict(_parse_subscriber_kv(kv) for kv in (subscribers or []))


def _parse_subscriber_kv(kv: str) -> tuple[str, str]:
    try:
        key, value = kv.split("=", maxsplit=1)
    except ValueError:
        raise click.ClickException(
            f"Invalid subscriber item: must have form `EVENT=URL`, but was {kv!r}"
        )
    return _parse_subscriber_event(key), _parse_subscriber_url(value)


def _parse_subscriber_event(key: str):
    norm_key = SUBSCRIBER_EVENTS.get(key)
    if norm_key is None:
        raise click.ClickException(
            "Invalid subscriber EVENT: must be one of "
            f"[{'|'.join(SUBSCRIBER_EVENTS.keys())}], but was {key!r}"
        )
    return norm_key


def _parse_subscriber_url(value: str):
    from urllib.parse import urlparse

    url = urlparse(value)
    if not all([url.scheme in ("http", "https"), url.netloc]):
        raise click.ClickException(f"Invalid subscriber URL: {value!r}")
    return value
