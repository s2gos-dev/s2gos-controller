#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import TypeAlias, Literal, Final

JSON_TYPES: Final = {"boolean", "integer", "number", "string", "array", "object"}

JsonType: TypeAlias = Literal[
    "boolean", "integer", "number", "string", "array", "object"
]
JsonValue: TypeAlias = (
    bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"] | None
)
JsonSchema: TypeAlias = dict[str, JsonValue]
