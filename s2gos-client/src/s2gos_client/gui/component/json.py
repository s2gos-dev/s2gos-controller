#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
from abc import ABC, abstractmethod
from types import NoneType
from typing import Any, Final, Literal, TypeAlias

JSON_TYPE_NAMES: Final = {"boolean", "integer", "number", "string", "array", "object"}

JsonType: TypeAlias = Literal[
    "boolean", "integer", "number", "string", "array", "object"
]
JsonValue: TypeAlias = (
    bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"] | None
)
JsonSchemaDict: TypeAlias = dict[str, JsonValue]


class JsonCodec(ABC):
    """Convert component values to/from JSON values."""

    @abstractmethod
    def from_json(self, value: Any) -> JsonValue:
        """Return a JSON value from given value."""

    @abstractmethod
    def to_json(self, json_value: JsonValue) -> Any:
        """Return a value from given JSON value."""


class JsonIdentityCodec(JsonCodec):
    def from_json(self, value: Any) -> JsonValue:
        assert isinstance(value, (bool, int, float, str, list, dict, NoneType))
        return value if value is not None else JSON_DEFAULT_VALUES[type(value)]

    def to_json(self, json_value: JsonValue) -> Any:
        assert isinstance(json_value, (bool, int, float, str, list, dict, NoneType))
        return json_value


class JsonDateCodec(JsonCodec):
    def from_json(self, value: datetime.date | None) -> str | None:
        assert isinstance(value, datetime.date)
        return datetime.date.isoformat(value)

    def to_json(self, json_value: str | None) -> datetime.date | None:
        if not json_value:
            return None
        assert isinstance(json_value, str)
        return datetime.date.fromisoformat(json_value)
